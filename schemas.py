"""
Pydantic 資料模型定義
定義 API 請求與回應的資料結構
支援多表設計的故事管理
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime

# 基礎資料結構
class ChapterOption(BaseModel):
    """章節選項"""
    text: str = Field(..., description="選項文字")
    next_id: int = Field(..., description="下一章節ID")

class GameState(BaseModel):
    """遊戲狀態"""
    class Config:
        extra = "allow"  # 允許額外的欄位

# 故事引擎相關
class StoryEngineRequest(BaseModel):
    """故事引擎請求"""
    game_state: Dict[str, Any] = Field(default_factory=dict, description="遊戲狀態物件")

class StoryEngineResponse(BaseModel):
    """故事引擎回應"""
    story_id: str = Field(..., description="故事ID")
    story_title: str = Field(..., description="故事標題")
    chapter_id: int = Field(..., description="章節ID")
    title: str = Field(..., description="章節標題")
    content: str = Field(..., description="章節內容（已處理條件內容）")
    options: List[Dict[str, Any]] = Field(..., description="可選擇的行動選項")

# 擲骰相關
class RollDiceRequest(BaseModel):
    """擲骰請求"""
    dice_count: int = Field(..., ge=1, le=100, description="骰子數量 (1-100)")
    dice_sides: int = Field(..., ge=2, le=100, description="骰子面數 (2-100)")
    modifier: int = Field(default=0, description="修正值")

class RollDiceResponse(BaseModel):
    """擲骰回應"""
    dice_count: int = Field(..., description="骰子數量")
    dice_sides: int = Field(..., description="骰子面數")
    modifier: int = Field(..., description="修正值")
    results: List[int] = Field(..., description="每顆骰子的結果")
    total: int = Field(..., description="總和（包含修正值）")
    description: str = Field(..., description="結果描述")

# 故事管理相關
class StoryInfo(BaseModel):
    """故事資訊"""
    story_id: str = Field(..., description="故事唯一識別ID")
    table_name: str = Field(..., description="資料表名稱")
    title: str = Field(..., description="故事標題")
    description: Optional[str] = Field(None, description="故事描述")
    author: Optional[str] = Field(None, description="作者")
    version: str = Field(default="1.0", description="版本號")
    is_active: str = Field(default="true", description="是否啟用")
    created_at: datetime = Field(..., description="建立時間")
    updated_at: Optional[datetime] = Field(None, description="更新時間")

class StoryListResponse(BaseModel):
    """故事列表回應"""
    stories: List[StoryInfo] = Field(..., description="故事列表")
    total: int = Field(..., description="總數量")

class ChapterInfo(BaseModel):
    """章節資訊"""
    id: int = Field(..., description="章節ID")
    title: str = Field(..., description="章節標題")
    content: str = Field(..., description="章節內容")
    options: List[Dict[str, Any]] = Field(..., description="選項列表")
    created_at: Optional[datetime] = Field(None, description="建立時間")

class StoryChaptersResponse(BaseModel):
    """故事章節列表回應"""
    story_id: str = Field(..., description="故事ID")
    story_title: str = Field(..., description="故事標題")
    chapters: List[ChapterInfo] = Field(..., description="章節列表")
    total: int = Field(..., description="章節總數")

# 故事建立和更新
class CreateStoryRequest(BaseModel):
    """建立故事請求"""
    story_id: str = Field(..., min_length=1, max_length=50, description="故事唯一識別ID（只能包含字母、數字、底線）")
    title: str = Field(..., min_length=1, max_length=255, description="故事標題")
    description: Optional[str] = Field(None, description="故事描述")
    author: Optional[str] = Field(None, description="作者")

class CreateStoryResponse(BaseModel):
    """建立故事回應"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="回應訊息")
    story_info: Optional[StoryInfo] = Field(None, description="故事資訊")

class ImportStoryRequest(BaseModel):
    """匯入故事請求"""
    story_id: str = Field(..., description="故事ID")
    title: str = Field(..., description="故事標題")
    description: Optional[str] = Field(None, description="故事描述")
    author: Optional[str] = Field(None, description="作者")
    chapters: List[Dict[str, Any]] = Field(..., description="章節資料")
    overwrite: bool = Field(default=False, description="是否覆蓋現有故事")

class ImportStoryResponse(BaseModel):
    """匯入故事回應"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="回應訊息")
    imported_chapters: int = Field(default=0, description="匯入的章節數量")

class ExportStoryResponse(BaseModel):
    """匯出故事回應"""
    story_id: str = Field(..., description="故事ID")
    title: str = Field(..., description="故事標題")
    description: Optional[str] = Field(None, description="故事描述")
    author: Optional[str] = Field(None, description="作者")
    version: str = Field(..., description="版本號")
    exported_at: datetime = Field(..., description="匯出時間")
    chapters: List[Dict[str, Any]] = Field(..., description="章節資料")

# 錯誤回應
class ErrorResponse(BaseModel):
    """錯誤回應"""
    error: str = Field(..., description="錯誤類型")
    message: str = Field(..., description="錯誤訊息")
    details: Optional[Dict[str, Any]] = Field(None, description="詳細資訊")

