#!/usr/bin/env python3
"""
資料庫遷移腳本：從單表設計遷移到多表設計
將現有的 chapters 表格資料遷移到新的多表架構
"""

import json
import sys
from sqlalchemy import text, inspect
from sqlalchemy.orm import Session
from models import SessionLocal, StoryRegistry, create_tables, create_story_table_in_db, register_story, engine

def check_old_table_exists():
    """檢查舊的 chapters 表格是否存在"""
    inspector = inspect(engine)
    return 'chapters' in inspector.get_table_names()

def migrate_from_single_table():
    """從單表架構遷移到多表架構"""
    
    print("🔄 開始資料庫遷移...")
    
    # 建立新的基礎資料表
    create_tables()
    print("✅ 建立基礎資料表完成")
    
    db = SessionLocal()
    try:
        # 檢查是否有舊的 chapters 表格
        if not check_old_table_exists():
            print("ℹ️  沒有發現舊的 chapters 表格，建立預設故事...")
            create_default_story(db)
            return
        
        print("📋 發現舊的 chapters 表格，開始遷移資料...")
        
        # 讀取舊表格資料
        result = db.execute(text("SELECT * FROM chapters ORDER BY id"))
        old_chapters = result.fetchall()
        
        if not old_chapters:
            print("ℹ️  舊表格沒有資料，建立預設故事...")
            create_default_story(db)
            return
        
        # 註冊預設故事
        story_id = "forest_adventure"
        if register_story(
            story_id=story_id,
            title="森林冒險",
            description="一個關於勇氣與智慧的森林探險故事",
            author="Story Engine Team"
        ):
            print(f"✅ 註冊故事: {story_id}")
        else:
            print(f"ℹ️  故事 {story_id} 已存在")
        
        # 遷移章節資料
        table_name = f"story_{story_id}"
        migrated_count = 0
        
        for chapter in old_chapters:
            # 將資料插入新的故事表格
            insert_sql = text(f"""
                INSERT INTO {table_name} (id, title, content, options, created_at)
                VALUES (:id, :title, :content, :options, :created_at)
            """)
            
            db.execute(insert_sql, {
                'id': chapter.id,
                'title': chapter.title,
                'content': chapter.content,
                'options': chapter.options,
                'created_at': chapter.created_at
            })
            migrated_count += 1
        
        db.commit()
        print(f"✅ 成功遷移 {migrated_count} 個章節到 {table_name}")
        
        # 詢問是否刪除舊表格
        response = input("🗑️  是否刪除舊的 chapters 表格？(y/N): ")
        if response.lower() == 'y':
            db.execute(text("DROP TABLE chapters"))
            db.commit()
            print("✅ 已刪除舊的 chapters 表格")
        else:
            print("ℹ️  保留舊的 chapters 表格")
            
    except Exception as e:
        print(f"❌ 遷移失敗: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()
    
    print("🎉 資料庫遷移完成！")

def create_default_story(db: Session):
    """建立預設故事"""
    story_id = "forest_adventure"
    
    # 註冊故事
    if register_story(
        story_id=story_id,
        title="森林冒險",
        description="一個關於勇氣與智慧的森林探險故事，包含豐富的遊戲狀態變數和條件內容",
        author="Story Engine Team"
    ):
        print(f"✅ 建立預設故事: {story_id}")
        
        # 匯入預設章節資料
        from seed_data import create_default_story_data
        chapters_data = create_default_story_data()
        
        table_name = f"story_{story_id}"
        imported_count = 0
        
        for chapter_data in chapters_data:
            insert_sql = text(f"""
                INSERT INTO {table_name} (id, title, content, options)
                VALUES (:id, :title, :content, :options)
            """)
            
            db.execute(insert_sql, {
                'id': chapter_data['id'],
                'title': chapter_data['title'],
                'content': chapter_data['content'],
                'options': json.dumps(chapter_data['options'], ensure_ascii=False)
            })
            imported_count += 1
        
        db.commit()
        print(f"✅ 匯入 {imported_count} 個預設章節")
    else:
        print(f"ℹ️  預設故事 {story_id} 已存在")

def create_sample_stories():
    """建立範例故事"""
    print("📚 建立範例故事...")
    
    # 太空奧德賽故事
    if register_story(
        story_id="space_odyssey",
        title="太空奧德賽",
        description="在浩瀚宇宙中尋找新家園的科幻冒險",
        author="Story Engine Team"
    ):
        print("✅ 建立範例故事: 太空奧德賽")
        
        # 建立簡單的範例章節
        db = SessionLocal()
        try:
            sample_chapters = [
                {
                    "id": 1,
                    "title": "太空站起始",
                    "content": "你站在太空站的觀景窗前，凝視著無盡的星空。作為探索隊的一員，你即將踏上尋找新家園的旅程。",
                    "options": [
                        {"text": "檢查太空船狀態", "next_id": 2},
                        {"text": "與隊友討論計劃", "next_id": 3}
                    ]
                },
                {
                    "id": 2,
                    "title": "太空船檢查",
                    "content": "你仔細檢查了太空船的各項系統，一切運作正常。現在可以開始你的星際之旅了。",
                    "options": []
                },
                {
                    "id": 3,
                    "title": "團隊會議",
                    "content": "與隊友的討論讓你對任務有了更清楚的認識。團隊合作將是成功的關鍵。",
                    "options": []
                }
            ]
            
            table_name = "story_space_odyssey"
            for chapter in sample_chapters:
                insert_sql = text(f"""
                    INSERT INTO {table_name} (id, title, content, options)
                    VALUES (:id, :title, :content, :options)
                """)
                
                db.execute(insert_sql, {
                    'id': chapter['id'],
                    'title': chapter['title'],
                    'content': chapter['content'],
                    'options': json.dumps(chapter['options'], ensure_ascii=False)
                })
            
            db.commit()
            print("✅ 匯入太空奧德賽章節")
        finally:
            db.close()

def main():
    """主要執行函數"""
    print("=" * 50)
    print("📦 Story Engine API - 資料庫遷移工具")
    print("=" * 50)
    
    try:
        # 執行遷移
        migrate_from_single_table()
        
        # 詢問是否建立範例故事
        response = input("📚 是否建立範例故事？(y/N): ")
        if response.lower() == 'y':
            create_sample_stories()
        
        print("\n🎉 所有操作完成！")
        print("💡 提示：")
        print("   - 使用 'python seed_data.py --list-stories' 查看所有故事")
        print("   - 使用 'python seed_data.py --export-story story_id' 匯出特定故事")
        print("   - 使用 'python seed_data.py --import-story story.json' 匯入新故事")
        
    except KeyboardInterrupt:
        print("\n⚠️  操作被使用者中斷")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 執行失敗: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

