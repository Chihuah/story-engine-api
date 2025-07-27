"""
FastAPI 主程式
互動式冒險故事引擎 API 服務
支援多表設計的故事管理
"""

import json
import random
import re
from datetime import datetime
from typing import Dict, Any, List

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from models import (
    SessionLocal, StoryRegistry, create_tables, get_story_table, 
    get_story_info, register_story, get_all_story_tables, get_db
)
from schemas import (
    StoryEngineRequest, StoryEngineResponse, RollDiceRequest, RollDiceResponse,
    StoryInfo, StoryListResponse, ChapterInfo, StoryChaptersResponse,
    CreateStoryRequest, CreateStoryResponse, ImportStoryRequest, ImportStoryResponse,
    ExportStoryResponse, ErrorResponse
)

# 建立 FastAPI 應用程式
app = FastAPI(
    title="Story Engine API",
    description="互動式冒險故事引擎 - 支援分支劇情、條件內容、遊戲狀態管理和擲骰檢定",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 自訂 OpenAPI schema 以減少 GPT Action 確認提示
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    from fastapi.openapi.utils import get_openapi
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # 為所有 API 端點添加 x-openai-isConsequential: false
    for path_item in openapi_schema.get("paths", {}).values():
        for operation in path_item.values():
            if isinstance(operation, dict) and "operationId" in operation:
                operation["x-openai-isConsequential"] = False
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# 設定 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化資料庫
create_tables()

def process_conditional_content(content: str, game_state: Dict[str, Any]) -> str:
    """處理條件內容標記，支援布林值和數值比較"""
    if not content:
        return ""
    
    # 處理 [[IF condition]]...[[ENDIF]] 語法
    def replace_condition(match):
        condition = match.group(1).strip()
        conditional_content = match.group(2)
        
        try:
            # 檢查是否為數值比較條件
            comparison_operators = ['>=', '<=', '>', '<', '==', '!=']
            for op in comparison_operators:
                if op in condition:
                    parts = condition.split(op, 1)
                    if len(parts) == 2:
                        var_name = parts[0].strip()
                        value_str = parts[1].strip()
                        
                        # 取得變數值
                        if var_name in game_state:
                            var_value = game_state[var_name]
                        else:
                            # 變數不存在時，數值變數預設為 0，布林變數預設為 False
                            var_value = 0
                        
                        # 嘗試將比較值轉換為數字
                        try:
                            compare_value = float(value_str)
                            var_value = float(var_value) if var_value is not None else 0
                        except (ValueError, TypeError):
                            # 如果無法轉換為數字，則進行字串比較
                            compare_value = value_str
                            var_value = str(var_value) if var_value is not None else ""
                        
                        # 執行比較
                        if op == '>':
                            result = var_value > compare_value
                        elif op == '<':
                            result = var_value < compare_value
                        elif op == '>=':
                            result = var_value >= compare_value
                        elif op == '<=':
                            result = var_value <= compare_value
                        elif op == '==':
                            result = var_value == compare_value
                        elif op == '!=':
                            result = var_value != compare_value
                        
                        return conditional_content if result else ""
                    break
            
            # 支援 NOT 條件（布林值）
            if condition.startswith("NOT "):
                var_name = condition[4:].strip()
                if var_name in game_state:
                    if not game_state[var_name]:
                        return conditional_content
                else:
                    # 變數不存在視為 false，所以 NOT false = true
                    return conditional_content
            
            # 支援基本的布林條件
            elif condition in game_state:
                if game_state[condition]:
                    return conditional_content
            
        except Exception as e:
            # 條件評估失敗時，記錄錯誤但不中斷處理
            print(f"條件評估錯誤: {condition} - {str(e)}")
        
        return ""
    
    # 使用正則表達式處理條件內容
    pattern = r'\[\[IF\s+([^\]]+)\]\](.*?)\[\[ENDIF\]\]'
    processed_content = re.sub(pattern, replace_condition, content, flags=re.DOTALL)
    
    return processed_content

# 故事管理 API
@app.get("/api/stories", response_model=StoryListResponse, tags=["故事管理"])
async def list_stories(db: Session = Depends(get_db)):
    """取得所有可用的故事列表"""
    try:
        stories = db.query(StoryRegistry).filter(StoryRegistry.is_active == "true").all()
        
        story_list = []
        for story in stories:
            story_info = StoryInfo(
                story_id=story.story_id,
                table_name=story.table_name,
                title=story.title,
                description=story.description,
                author=story.author,
                version=story.version,
                is_active=story.is_active,
                created_at=story.created_at,
                updated_at=story.updated_at
            )
            story_list.append(story_info)
        
        return StoryListResponse(stories=story_list, total=len(story_list))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取得故事列表失敗: {str(e)}")

@app.get("/api/stories/{story_id}", response_model=StoryInfo, tags=["故事管理"])
async def get_story(story_id: str, db: Session = Depends(get_db)):
    """取得特定故事的詳細資訊"""
    story = db.query(StoryRegistry).filter(
        StoryRegistry.story_id == story_id,
        StoryRegistry.is_active == "true"
    ).first()
    
    if not story:
        raise HTTPException(status_code=404, detail="故事不存在")
    
    return StoryInfo(
        story_id=story.story_id,
        table_name=story.table_name,
        title=story.title,
        description=story.description,
        author=story.author,
        version=story.version,
        is_active=story.is_active,
        created_at=story.created_at,
        updated_at=story.updated_at
    )

@app.get("/api/stories/{story_id}/chapters", response_model=StoryChaptersResponse, tags=["故事管理"])
async def get_story_chapters(story_id: str, db: Session = Depends(get_db)):
    """取得故事的所有章節"""
    # 驗證故事存在
    story = db.query(StoryRegistry).filter(
        StoryRegistry.story_id == story_id,
        StoryRegistry.is_active == "true"
    ).first()
    
    if not story:
        raise HTTPException(status_code=404, detail="故事不存在")
    
    # 查詢章節
    try:
        table_name = story.table_name
        result = db.execute(text(f"SELECT * FROM {table_name} ORDER BY id"))
        chapters = result.fetchall()
        
        chapter_list = []
        for chapter in chapters:
            # 檢查 options 的類型，如果已經是 list/dict 就直接使用，否則解析 JSON
            if isinstance(chapter.options, str):
                options = json.loads(chapter.options) if chapter.options else []
            else:
                options = chapter.options if chapter.options else []
                
            chapter_info = ChapterInfo(
                id=chapter.id,
                title=chapter.title,
                content=chapter.content,
                options=options,
                created_at=chapter.created_at if hasattr(chapter, 'created_at') else None
            )
            chapter_list.append(chapter_info)
        
        return StoryChaptersResponse(
            story_id=story_id,
            story_title=story.title,
            chapters=chapter_list,
            total=len(chapter_list)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取得章節列表失敗: {str(e)}")

# 故事引擎 API
@app.post("/api/story_engine/{story_id}/{chapter_id}", response_model=StoryEngineResponse, tags=["故事引擎"])
async def get_story_chapter(
    story_id: str,
    chapter_id: int,
    request: StoryEngineRequest,
    db: Session = Depends(get_db)
):
    """載入指定故事的章節內容"""
    
    # 驗證故事存在
    story = db.query(StoryRegistry).filter(
        StoryRegistry.story_id == story_id,
        StoryRegistry.is_active == "true"
    ).first()
    
    if not story:
        raise HTTPException(status_code=404, detail="故事不存在")
    
    # 查詢章節
    try:
        table_name = story.table_name
        result = db.execute(
            text(f"SELECT * FROM {table_name} WHERE id = :chapter_id"),
            {"chapter_id": chapter_id}
        )
        chapter = result.fetchone()
        
        if not chapter:
            raise HTTPException(status_code=404, detail="章節不存在")
        
        # 處理條件內容
        processed_content = process_conditional_content(chapter.content, request.game_state)
        
        # 解析選項 - 檢查類型後決定是否需要解析 JSON
        if isinstance(chapter.options, str):
            options = json.loads(chapter.options) if chapter.options else []
        else:
            options = chapter.options if chapter.options else []
        
        return StoryEngineResponse(
            story_id=story_id,
            story_title=story.title,
            chapter_id=chapter_id,
            title=chapter.title,
            content=processed_content,
            options=options
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"載入章節失敗: {str(e)}")

# 向後相容的 API（使用預設故事）
@app.post("/api/story_engine/{chapter_id}", response_model=StoryEngineResponse, tags=["故事引擎"])
async def get_chapter_legacy(
    chapter_id: int,
    request: StoryEngineRequest,
    db: Session = Depends(get_db)
):
    """向後相容的章節載入 API（使用預設故事）"""
    # 取得第一個啟用的故事作為預設故事
    default_story = db.query(StoryRegistry).filter(StoryRegistry.is_active == "true").first()
    
    if not default_story:
        raise HTTPException(status_code=404, detail="沒有可用的故事")
    
    return await get_story_chapter(default_story.story_id, chapter_id, request, db)

# 擲骰 API
@app.post("/api/roll_dice", response_model=RollDiceResponse, tags=["擲骰系統"])
async def roll_dice(request: RollDiceRequest):
    """執行擲骰子檢定"""
    
    # 執行擲骰
    results = []
    for _ in range(request.dice_count):
        roll = random.randint(1, request.dice_sides)
        results.append(roll)
    
    # 計算總和
    total = sum(results) + request.modifier
    
    # 生成描述
    if request.dice_count == 1:
        description = f"1D{request.dice_sides}"
    else:
        description = f"{request.dice_count}D{request.dice_sides}"
    
    if request.modifier != 0:
        if request.modifier > 0:
            description += f"+{request.modifier}"
        else:
            description += f"{request.modifier}"
    
    description += f" = {total}"
    
    return RollDiceResponse(
        dice_count=request.dice_count,
        dice_sides=request.dice_sides,
        modifier=request.modifier,
        results=results,
        total=total,
        description=description
    )

# 故事建立 API
@app.post("/api/stories", response_model=CreateStoryResponse, tags=["故事管理"])
async def create_story(request: CreateStoryRequest, db: Session = Depends(get_db)):
    """建立新故事"""
    
    # 驗證 story_id 格式
    if not re.match(r'^[a-zA-Z0-9_]+$', request.story_id):
        raise HTTPException(
            status_code=400, 
            detail="故事ID只能包含字母、數字和底線"
        )
    
    # 註冊故事
    success = register_story(
        story_id=request.story_id,
        title=request.title,
        description=request.description,
        author=request.author
    )
    
    if not success:
        return CreateStoryResponse(
            success=False,
            message="故事ID已存在"
        )
    
    # 取得建立的故事資訊
    story = db.query(StoryRegistry).filter(StoryRegistry.story_id == request.story_id).first()
    
    story_info = StoryInfo(
        story_id=story.story_id,
        table_name=story.table_name,
        title=story.title,
        description=story.description,
        author=story.author,
        version=story.version,
        is_active=story.is_active,
        created_at=story.created_at,
        updated_at=story.updated_at
    )
    
    return CreateStoryResponse(
        success=True,
        message="故事建立成功",
        story_info=story_info
    )

# 故事匯出 API
@app.get("/api/stories/{story_id}/export", response_model=ExportStoryResponse, tags=["故事管理"])
async def export_story(story_id: str, db: Session = Depends(get_db)):
    """匯出故事為 JSON 格式"""
    
    # 驗證故事存在
    story = db.query(StoryRegistry).filter(
        StoryRegistry.story_id == story_id,
        StoryRegistry.is_active == "true"
    ).first()
    
    if not story:
        raise HTTPException(status_code=404, detail="故事不存在")
    
    # 查詢章節
    try:
        table_name = story.table_name
        result = db.execute(text(f"SELECT * FROM {table_name} ORDER BY id"))
        chapters = result.fetchall()
        
        chapter_list = []
        for chapter in chapters:
            # 檢查 options 的類型，如果已經是 list/dict 就直接使用，否則解析 JSON
            if isinstance(chapter.options, str):
                options = json.loads(chapter.options) if chapter.options else []
            else:
                options = chapter.options if chapter.options else []
                
            chapter_data = {
                "id": chapter.id,
                "title": chapter.title,
                "content": chapter.content,
                "options": options
            }
            chapter_list.append(chapter_data)
        
        return ExportStoryResponse(
            story_id=story_id,
            title=story.title,
            description=story.description,
            author=story.author,
            version=story.version,
            exported_at=datetime.now(),
            chapters=chapter_list
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"匯出故事失敗: {str(e)}")

# 隱私權政策
@app.get("/privacy", response_class=HTMLResponse, tags=["隱私權政策"])
async def privacy_policy():
    """隱私權政策頁面"""
    try:
        with open("privacy-policy.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        # 如果檔案不存在，回傳簡化版
        return """
        <!DOCTYPE html>
            <html lang="zh-TW">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>隱私權政策 - 互動式冒險故事引擎</title>
                <style>
                    body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; line-height: 1.6; }
                    h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
                    h2 { color: #34495e; margin-top: 30px; }
                    .highlight { background-color: #e8f4fd; padding: 15px; border-left: 4px solid #3498db; margin: 20px 0; }
                </style>
            </head>
            <body>
                <h1>隱私權政策</h1>
                <p><strong>互動式冒險故事引擎 API 服務</strong></p>
                
                <div class="highlight">
                    <strong>重要聲明：</strong>我們致力於保護您的隱私，僅收集提供服務所必需的最少資料，且不會收集任何個人識別資訊。
                </div>

                <h2>資料收集</h2>
                <p>我們的故事引擎 API 僅收集遊戲進行所需的最少資料：</p>
                <ul>
                    <li>故事章節請求（章節 ID）</li>
                    <li>遊戲狀態變數（如 has_key: true）</li>
                    <li>擲骰請求參數</li>
                </ul>

                <h2>資料使用</h2>
                <p>收集的資料僅用於：</p>
                <ul>
                    <li>提供故事內容回應</li>
                    <li>處理遊戲邏輯</li>
                    <li>執行擲骰計算</li>
                </ul>

                <h2>資料保護</h2>
                <ul>
                    <li>我們不儲存用戶的個人識別資訊</li>
                    <li>所有通訊都透過 HTTPS 加密</li>
                    <li>遊戲狀態僅在請求期間暫時處理</li>
                </ul>

                <h2>資料保存</h2>
                <ul>
                    <li>我們不永久儲存用戶的遊戲資料</li>
                    <li>每次 API 呼叫都是獨立的，不保留歷史記錄</li>
                    <li>伺服器日誌會定期清理</li>
                </ul>

                <h2>聯絡資訊</h2>
                <p>如有隱私權相關問題，請透過專案 GitHub 頁面聯絡我們。</p>

                <p><strong>最後更新：</strong> 2024年7月26日</p>
            </body>
            </html>
        """
    except Exception as e:
        return f"""
        <!DOCTYPE html>
        <html lang="zh-TW">
        <head>
            <meta charset="UTF-8">
            <title>隱私權政策載入錯誤</title>
        </head>
        <body>
            <h1>隱私權政策</h1>
            <p>抱歉，隱私權政策頁面暫時無法載入。</p>
            <p>錯誤資訊：{str(e)}</p>
        </body>
        </html>
        """

# 根路徑
@app.get("/", tags=["系統資訊"])
async def root():
    """API 根路徑"""
    return {
        "message": "Story Engine API",
        "version": "1.1.0",
        "description": "互動式冒險故事引擎 - 支援多故事管理",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# 健康檢查
@app.get("/health", tags=["系統資訊"])
async def health_check():
    """健康檢查端點"""
    return {"status": "healthy", "timestamp": datetime.now()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

