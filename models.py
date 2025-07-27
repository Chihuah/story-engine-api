"""
SQLAlchemy
資料庫模型定義
使用 SQLAlchemy ORM 定義資料表結構
支援多表設計：每個故事使用獨立的資料表
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, JSON, DateTime, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from typing import Dict, List, Optional
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

# 建立資料庫引擎
engine = create_engine(DATABASE_URL)

# 建立 Session 類別
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 建立基礎模型類別
Base = declarative_base()

class StoryRegistry(Base):
    """故事註冊表 - 管理所有故事的元資料"""
    __tablename__ = "story_registry"
    
    story_id = Column(String(50), primary_key=True, index=True)
    table_name = Column(String(100), nullable=False, unique=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    author = Column(String(255))
    version = Column(String(50), default="1.0")
    is_active = Column(String(10), default="true")  # 使用字串避免 SQLite 布林值問題
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

def create_story_table(story_id: str) -> Table:
    """動態建立故事表格"""
    table_name = f"story_{story_id}"
    
    story_table = Table(
        table_name,
        Base.metadata,
        Column('id', Integer, primary_key=True, index=True),
        Column('title', String(255), nullable=False),
        Column('content', Text, nullable=False),
        Column('options', JSON),
        Column('created_at', DateTime, server_default=func.now()),
        extend_existing=True
    )
    
    return story_table

def get_story_table(story_id: str) -> Optional[Table]:
    """取得故事表格物件"""
    table_name = f"story_{story_id}"
    
    # 檢查表格是否存在於 metadata 中
    if table_name in Base.metadata.tables:
        return Base.metadata.tables[table_name]
    
    # 如果不存在，嘗試從資料庫反射
    try:
        metadata = MetaData()
        metadata.reflect(bind=engine, only=[table_name])
        if table_name in metadata.tables:
            # 將反射的表格加入到 Base.metadata 中
            table = metadata.tables[table_name]
            Base.metadata._add_table(table, replace=True)
            return table
    except Exception:
        pass
    
    return None

def create_story_table_in_db(story_id: str):
    """在資料庫中建立故事表格"""
    story_table = create_story_table(story_id)
    story_table.create(engine, checkfirst=True)
    return story_table

def get_all_story_tables() -> List[str]:
    """取得所有故事表格名稱"""
    db = SessionLocal()
    try:
        registries = db.query(StoryRegistry).filter(StoryRegistry.is_active == "true").all()
        return [registry.table_name for registry in registries]
    finally:
        db.close()

def get_story_info(story_id: str) -> Optional[StoryRegistry]:
    """取得故事資訊"""
    db = SessionLocal()
    try:
        return db.query(StoryRegistry).filter(StoryRegistry.story_id == story_id).first()
    finally:
        db.close()

def register_story(story_id: str, title: str, description: str = None, author: str = None) -> bool:
    """註冊新故事"""
    db = SessionLocal()
    try:
        # 檢查故事是否已存在
        existing = db.query(StoryRegistry).filter(StoryRegistry.story_id == story_id).first()
        if existing:
            return False
        
        # 建立註冊記錄
        table_name = f"story_{story_id}"
        registry = StoryRegistry(
            story_id=story_id,
            table_name=table_name,
            title=title,
            description=description,
            author=author
        )
        
        db.add(registry)
        db.commit()
        
        # 建立對應的資料表
        create_story_table_in_db(story_id)
        
        return True
    except Exception as e:
        db.rollback()
        print(f"註冊故事失敗: {e}")
        return False
    finally:
        db.close()

def get_db():
    """取得資料庫 Session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    
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

