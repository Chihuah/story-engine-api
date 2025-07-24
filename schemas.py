"""
Pydantic 資料模型定義
定義 API 請求與回應的資料結構
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

class StoryEngineRequest(BaseModel):
    """故事引擎 API 請求模型"""
    chapter_id: int = Field(..., description="章節 ID", example=1)
    game_state: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="遊戲狀態變數", 
        example={"found_secret_path": True, "has_key": False}
    )

class StoryOption(BaseModel):
    """故事選項模型"""
    text: str = Field(..., description="選項文字", example="冷靜說服")
    next_id: int = Field(..., description="下一章節 ID", example=6)

class StoryEngineResponse(BaseModel):
    """故事引擎 API 回應模型"""
    chapter_id: int = Field(..., description="當前章節 ID", example=3)
    title: str = Field(..., description="章節標題", example="探索王宮")
    content: str = Field(..., description="章節內容", example="你們進入了長廊...")
    options: List[StoryOption] = Field(
        default=[], 
        description="可選擇的選項列表"
    )
    game_state: Dict[str, Any] = Field(
        default={}, 
        description="更新後的遊戲狀態"
    )

class RollDiceRequest(BaseModel):
    """擲骰子 API 請求模型"""
    dice_sides: int = Field(..., description="骰子面數", example=6, ge=2, le=100)
    dice_count: int = Field(..., description="骰子數量", example=2, ge=1, le=100)

class RollDiceResponse(BaseModel):
    """擲骰子 API 回應模型"""
    rolls: List[int] = Field(..., description="每次擲骰的結果", example=[5, 3])
    total: int = Field(..., description="總和", example=8)
    description: str = Field(..., description="擲骰描述", example="2D6 擲出的結果")

# 錯誤回應模型
class ErrorResponse(BaseModel):
    """錯誤回應模型"""
    error: str = Field(..., description="錯誤訊息", example="找不到第 99 章")

