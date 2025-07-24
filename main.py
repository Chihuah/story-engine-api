"""
GPTs 互動式冒險故事引擎 - FastAPI 主程式
支援 story_engine 和 roll_dice 兩個核心 API
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
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

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

