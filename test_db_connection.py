#!/usr/bin/env python3
"""
資料庫連線測試工具
測試多表資料庫架構的連線和基本功能
支援: 多表設計 + 故事註冊表 + 動態表創建
"""

import os
import sys
import asyncio
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from models import Base, StoryRegistry, get_story_table_class
from main import get_database_url
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseTester:
    """資料庫測試類別"""
    
    def __init__(self):
        self.database_url = get_database_url()
        self.engine = None
        self.async_engine = None
        self.session = None
        
    def setup_engines(self):
        """設定資料庫引擎"""
        try:
            # 同步引擎
            if self.database_url.startswith('sqlite'):
                self.engine = create_engine(self.database_url, echo=False)
            else:
                self.engine = create_engine(self.database_url, echo=False, pool_pre_ping=True)
            
            # 異步引擎（如果需要）
            async_url = self.database_url.replace('postgresql://', 'postgresql+asyncpg://')
            if not async_url.startswith('sqlite'):
                self.async_engine = create_async_engine(async_url, echo=False)
            
            logger.info("✅ 資料庫引擎設定成功")
            return True
            
        except Exception as e:
            logger.error(f"❌ 資料庫引擎設定失敗: {e}")
            return False
    
    def test_basic_connection(self):
        """測試基本連線"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                if result.fetchone()[0] == 1:
                    logger.info("✅ 基本資料庫連線測試通過")
                    return True
                else:
                    logger.error("❌ 基本連線測試失敗")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ 資料庫連線失敗: {e}")
            return False
    
    def test_database_info(self):
        """測試資料庫資訊"""
        try:
            with self.engine.connect() as conn:
                # 檢查資料庫類型
                if self.database_url.startswith('sqlite'):
                    db_type = "SQLite"
                    result = conn.execute(text("SELECT sqlite_version()"))
                    version = result.fetchone()[0]
                elif self.database_url.startswith('postgresql'):
                    db_type = "PostgreSQL"
                    result = conn.execute(text("SELECT version()"))
                    version = result.fetchone()[0].split()[1]
                else:
                    db_type = "Unknown"
                    version = "Unknown"
                
                logger.info(f"📊 資料庫類型: {db_type}")
                logger.info(f"📊 資料庫版本: {version}")
                logger.info(f"📊 連線 URL: {self.database_url.split('@')[0]}@***")
                
                return True
                
        except Exception as e:
            logger.error(f"❌ 無法獲取資料庫資訊: {e}")
            return False
    
    def test_create_tables(self):
        """測試建立資料表"""
        try:
            # 建立所有表格
            Base.metadata.create_all(bind=self.engine)
            logger.info("✅ 資料表建立成功")
            
            # 檢查表格是否存在
            inspector = inspect(self.engine)
            tables = inspector.get_table_names()
            
            # 檢查故事註冊表
            if 'story_registry' in tables:
                logger.info("✅ 故事註冊表 (story_registry) 存在")
            else:
                logger.warning("⚠️ 故事註冊表不存在")
            
            logger.info(f"📊 現有資料表: {tables}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 建立資料表失敗: {e}")
            return False
    
    def test_story_registry_operations(self):
        """測試故事註冊表操作"""
        try:
            Session = sessionmaker(bind=self.engine)
            session = Session()
            
            # 測試插入故事註冊資料
            test_story = StoryRegistry(
                story_id="test_story",
                table_name="story_test_story",
                title="測試故事",
                description="這是一個測試故事",
                author="測試作者",
                version="1.0"
            )
            
            # 檢查是否已存在
            existing = session.query(StoryRegistry).filter_by(story_id="test_story").first()
            if existing:
                session.delete(existing)
                session.commit()
                logger.info("🧹 清除現有測試資料")
            
            # 插入新資料
            session.add(test_story)
            session.commit()
            logger.info("✅ 故事註冊資料插入成功")
            
            # 測試查詢
            retrieved = session.query(StoryRegistry).filter_by(story_id="test_story").first()
            if retrieved and retrieved.title == "測試故事":
                logger.info("✅ 故事註冊資料查詢成功")
            else:
                logger.error("❌ 故事註冊資料查詢失敗")
                return False
            
            # 測試更新
            retrieved.description = "更新後的測試故事描述"
            session.commit()
            logger.info("✅ 故事註冊資料更新成功")
            
            # 清除測試資料
            session.delete(retrieved)
            session.commit()
            logger.info("🧹 測試資料清除完成")
            
            session.close()
            return True
            
        except Exception as e:
            logger.error(f"❌ 故事註冊表操作失敗: {e}")
            return False
    
    def test_dynamic_story_table(self):
        """測試動態故事表創建"""
        try:
            # 創建測試故事表
            story_table_class = get_story_table_class("test_story")
            story_table_class.__table__.create(bind=self.engine, checkfirst=True)
            logger.info("✅ 動態故事表創建成功")
            
            # 測試插入資料
            Session = sessionmaker(bind=self.engine)
            session = Session()
            
            test_chapter = story_table_class(
                id=1,
                title="測試章節",
                content="這是一個測試章節的內容",
                options=[
                    {
                        "text": "選項一",
                        "next_chapter": 2,
                        "condition": None,
                        "game_state": {"test_var": True}
                    }
                ]
            )
            
            session.add(test_chapter)
            session.commit()
            logger.info("✅ 故事章節資料插入成功")
            
            # 測試查詢
            retrieved = session.query(story_table_class).filter_by(id=1).first()
            if retrieved and retrieved.title == "測試章節":
                logger.info("✅ 故事章節資料查詢成功")
                logger.info(f"📊 章節選項: {retrieved.options}")
            else:
                logger.error("❌ 故事章節資料查詢失敗")
                return False
            
            # 清除測試資料
            session.delete(retrieved)
            session.commit()
            session.close()
            
            # 刪除測試表
            story_table_class.__table__.drop(bind=self.engine, checkfirst=True)
            logger.info("🧹 測試故事表清除完成")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 動態故事表測試失敗: {e}")
            return False
    
    def test_json_operations(self):
        """測試 JSON 欄位操作"""
        try:
            # 創建測試故事表
            story_table_class = get_story_table_class("json_test")
            story_table_class.__table__.create(bind=self.engine, checkfirst=True)
            
            Session = sessionmaker(bind=self.engine)
            session = Session()
            
            # 測試複雜的 JSON 資料
            complex_options = [
                {
                    "text": "使用魔法攻擊",
                    "next_chapter": 10,
                    "condition": "magic_power >= 50 AND has_staff",
                    "game_state": {
                        "magic_power": -20,
                        "used_magic": True,
                        "battle_style": "aggressive"
                    },
                    "description": "消耗魔力發動強力攻擊"
                },
                {
                    "text": "物理攻擊",
                    "next_chapter": 11,
                    "condition": "strength > 15",
                    "game_state": {
                        "stamina": -10,
                        "battle_style": "physical"
                    }
                }
            ]
            
            test_chapter = story_table_class(
                id=1,
                title="戰鬥章節",
                content="你面對著強大的敵人，[[IF has_staff]]你的法杖閃閃發光[[ENDIF]]。",
                options=complex_options
            )
            
            session.add(test_chapter)
            session.commit()
            logger.info("✅ 複雜 JSON 資料插入成功")
            
            # 查詢並驗證 JSON 資料
            retrieved = session.query(story_table_class).filter_by(id=1).first()
            if retrieved:
                options = retrieved.options
                if len(options) == 2 and options[0]["text"] == "使用魔法攻擊":
                    logger.info("✅ JSON 資料查詢和解析成功")
                    logger.info(f"📊 第一個選項條件: {options[0]['condition']}")
                    logger.info(f"📊 第一個選項狀態變更: {options[0]['game_state']}")
                else:
                    logger.error("❌ JSON 資料解析不正確")
                    return False
            else:
                logger.error("❌ JSON 資料查詢失敗")
                return False
            
            # 清除測試資料
            session.delete(retrieved)
            session.commit()
            session.close()
            
            # 刪除測試表
            story_table_class.__table__.drop(bind=self.engine, checkfirst=True)
            logger.info("🧹 JSON 測試表清除完成")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ JSON 操作測試失敗: {e}")
            return False
    
    def test_performance(self):
        """測試資料庫效能"""
        try:
            import time
            
            # 測試連線時間
            start_time = time.time()
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            connection_time = (time.time() - start_time) * 1000
            
            logger.info(f"📊 連線時間: {connection_time:.2f} ms")
            
            if connection_time < 1000:  # 1秒內
                logger.info("✅ 連線效能良好")
            else:
                logger.warning("⚠️ 連線時間較長，可能需要優化")
            
            # 測試查詢效能
            Session = sessionmaker(bind=self.engine)
            session = Session()
            
            start_time = time.time()
            stories = session.query(StoryRegistry).all()
            query_time = (time.time() - start_time) * 1000
            
            logger.info(f"📊 查詢時間: {query_time:.2f} ms")
            logger.info(f"📊 故事數量: {len(stories)}")
            
            session.close()
            return True
            
        except Exception as e:
            logger.error(f"❌ 效能測試失敗: {e}")
            return False
    
    def run_all_tests(self):
        """執行所有測試"""
        logger.info("🚀 開始資料庫連線測試")
        logger.info("=" * 50)
        
        tests = [
            ("設定資料庫引擎", self.setup_engines),
            ("基本連線測試", self.test_basic_connection),
            ("資料庫資訊檢查", self.test_database_info),
            ("建立資料表", self.test_create_tables),
            ("故事註冊表操作", self.test_story_registry_operations),
            ("動態故事表測試", self.test_dynamic_story_table),
            ("JSON 欄位操作", self.test_json_operations),
            ("效能測試", self.test_performance)
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            logger.info(f"\n🧪 執行測試: {test_name}")
            try:
                if test_func():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                logger.error(f"❌ 測試異常: {e}")
                failed += 1
        
        logger.info("\n" + "=" * 50)
        logger.info("📊 測試結果總結")
        logger.info(f"✅ 通過: {passed}")
        logger.info(f"❌ 失敗: {failed}")
        logger.info(f"📊 總計: {passed + failed}")
        
        if failed == 0:
            logger.info("🎉 所有測試都通過了！資料庫連線正常。")
            return True
        else:
            logger.error(f"⚠️ 有 {failed} 個測試失敗，請檢查資料庫設定。")
            return False

def main():
    """主函數"""
    print("🔧 Story Engine Database Connection Tester v2.0")
    print("支援多表資料庫架構和動態表創建")
    print("=" * 60)
    
    # 檢查環境變數
    database_url = get_database_url()
    if not database_url:
        print("❌ 錯誤: 未設定 DATABASE_URL 環境變數")
        print("請設定環境變數或建立 .env 檔案")
        sys.exit(1)
    
    # 執行測試
    tester = DatabaseTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎯 建議下一步:")
        print("1. 執行 python seed_data.py 載入範例故事")
        print("2. 執行 python test_api.py 測試 API 功能")
        print("3. 啟動服務: uvicorn main:app --reload")
        sys.exit(0)
    else:
        print("\n🔧 故障排除建議:")
        print("1. 檢查 DATABASE_URL 設定是否正確")
        print("2. 確認資料庫服務是否正在運行")
        print("3. 檢查網路連線和防火牆設定")
        print("4. 查看詳細錯誤日誌")
        sys.exit(1)

if __name__ == "__main__":
    main()

