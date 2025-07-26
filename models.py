"""
SQLAlchemy 資料庫模型定義
包含 Chapter 模型和資料庫連線設定
"""

from sqlalchemy import create_engine, Column, Integer, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

from dotenv import load_dotenv, find_dotenv

"""顯示環境資訊"""
# 嘗試載入 .env 檔案
dotenv_path = find_dotenv()
if dotenv_path:
    print(f"載入的 .env 檔案路徑: {dotenv_path}")
    load_dotenv(dotenv_path, override=True)
else:
    print("未找到 .env 檔案")

# 資料庫連線設定
DATABASE_URL = os.environ.get('DATABASE_URL')
print(f"   DATABASE_URL: {os.environ.get('DATABASE_URL', '未設定')}")
# # 處理 Render PostgreSQL URL 格式
# if DATABASE_URL.startswith("postgres://"):
#     DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 建立資料庫引擎
engine = create_engine(DATABASE_URL)

# 建立 Session 類別
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 建立基礎模型類別
Base = declarative_base()

class Chapter(Base):
    """
    故事章節模型
    儲存章節標題、內容和選項資料
    """
    __tablename__ = "story_chapters"
    
    id = Column(Integer, primary_key=True, index=True, comment="章節 ID")
    title = Column(Text, nullable=False, comment="章節標題")
    content = Column(Text, nullable=False, comment="章節內容")
    options = Column(Text, nullable=True, comment="選項 JSON 字串")
    created_at = Column(DateTime, default=datetime.utcnow, comment="建立時間")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新時間")
    
    def __repr__(self):
        return f"<Chapter(id={self.id}, title='{self.title[:20]}...')>"
    
    def to_dict(self):
        """轉換為字典格式"""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "options": self.options,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

# 建立所有資料表的函數
def create_tables():
    """建立所有資料表"""
    DATABASE_URL = os.environ.get("DATABASE_URL")
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    print("資料表建立完成")

# 取得資料庫 Session 的函數
def get_database_session():
    """取得資料庫 Session"""
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        db.close()
        raise e

if __name__ == "__main__":
    # 直接執行此檔案時建立資料表
    create_tables()

