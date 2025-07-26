"""
GPTs 互動式冒險故事引擎 - FastAPI 主程式
支援 story_engine 和 roll_dice 兩個核心 API
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import json
import random
import re
import os
from typing import Dict, Any, Optional, List

from models import SessionLocal, engine, Chapter
from schemas import StoryEngineRequest, StoryEngineResponse, RollDiceRequest, RollDiceResponse

# 建立資料表
from models import Base
Base.metadata.create_all(bind=engine)

# 建立 FastAPI 應用程式
app = FastAPI(
    title="GPTs 互動式冒險故事引擎",
    description="支援章節載入與擲骰檢定的故事引擎 API",
    version="1.0.0"
)

# 設定 CORS - 允許所有來源
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 資料庫依賴注入
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def root():
    """根路徑 - API 狀態檢查"""
    return {
        "message": "GPTs 互動式冒險故事引擎 API",
        "version": "1.0.0",
        "endpoints": ["/story_engine", "/roll_dice", "/docs"]
    }

@app.get("/health")
async def health_check():
    """健康檢查端點"""
    return {"status": "healthy", "service": "story-engine-api"}

def parse_conditional_content(content: str, game_state: Dict[str, Any]) -> str:
    """
    解析內容中的條件區塊 [[IF condition]]...[[ENDIF]]
    根據 game_state 決定是否顯示該區塊內容
    """
    if not game_state:
        # 如果沒有 game_state，移除所有條件區塊
        return re.sub(r'\[\[IF\s+\w+\]\].*?\[\[ENDIF\]\]', '', content, flags=re.DOTALL)
    
    def replace_conditional(match):
        condition = match.group(1).strip()
        block_content = match.group(2)
        
        # 檢查條件是否在 game_state 中且為 True
        if condition in game_state and game_state[condition]:
            return block_content
        else:
            return ""
    
    # 使用正則表達式處理條件區塊
    pattern = r'\[\[IF\s+(\w+)\]\](.*?)\[\[ENDIF\]\]'
    result = re.sub(pattern, replace_conditional, content, flags=re.DOTALL)
    
    return result

@app.post("/story_engine", response_model=StoryEngineResponse)
async def story_engine(request: StoryEngineRequest, db: Session = Depends(get_db)):
    """
    故事引擎 API - 載入章節內容與選項
    支援 game_state 條件內容解析
    """
    try:
        # 查詢章節
        chapter = db.query(Chapter).filter(Chapter.id == request.chapter_id).first()
        
        if not chapter:
            raise HTTPException(
                status_code=404, 
                detail=f"找不到第 {request.chapter_id} 章"
            )
        
        # 解析條件內容
        processed_content = parse_conditional_content(chapter.content, request.game_state or {})
        
        # 解析選項 JSON
        options = []
        if chapter.options:
            try:
                options = json.loads(chapter.options)
            except json.JSONDecodeError:
                # 如果 JSON 解析失敗，返回空選項列表
                options = []
        
        # 建立回應
        response = StoryEngineResponse(
            chapter_id=chapter.id,
            title=chapter.title,
            content=processed_content,
            options=options,
            game_state=request.game_state or {}
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"伺服器錯誤: {str(e)}")

@app.post("/roll_dice", response_model=RollDiceResponse)
async def roll_dice(request: RollDiceRequest):
    """
    擲骰子 API - 支援多面數與多顆骰子
    """
    try:
        # 驗證輸入參數
        if request.dice_sides <= 1:
            raise HTTPException(
                status_code=400, 
                detail="骰子面數必須大於 1"
            )
        
        if request.dice_count <= 0:
            raise HTTPException(
                status_code=400, 
                detail="骰子數量必須大於 0"
            )
        
        if request.dice_count > 100:
            raise HTTPException(
                status_code=400, 
                detail="骰子數量不能超過 100"
            )
        
        # 執行擲骰
        rolls = []
        for _ in range(request.dice_count):
            roll = random.randint(1, request.dice_sides)
            rolls.append(roll)
        
        total = sum(rolls)
        
        # 建立描述
        if request.dice_count == 1:
            description = f"1D{request.dice_sides} 擲出的結果"
        else:
            description = f"{request.dice_count}D{request.dice_sides} 擲出的結果"
        
        response = RollDiceResponse(
            rolls=rolls,
            total=total,
            description=description
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"伺服器錯誤: {str(e)}")

@app.get("/privacy", response_class=HTMLResponse, tags=["隱私權政策"])
async def privacy_policy():
    """
    隱私權政策頁面
    
    回傳完整的隱私權政策 HTML 頁面，用於滿足 GPT Action 的隱私權政策要求。
    """
    try:
        # 嘗試讀取隱私權政策 HTML 檔案
        privacy_file_path = os.path.join(os.path.dirname(__file__), "privacy-policy.html")
        
        if os.path.exists(privacy_file_path):
            with open(privacy_file_path, "r", encoding="utf-8") as f:
                return f.read()
        else:
            # 如果檔案不存在，回傳基本的隱私權政策內容
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
        # 如果發生錯誤，回傳簡單的錯誤頁面
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

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

