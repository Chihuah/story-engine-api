"""
故事資料管理工具
支援多表設計的故事匯入、匯出、驗證和管理功能
"""

import json
import os
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session
from models import (
    SessionLocal, StoryRegistry, create_tables, register_story, 
    get_story_info, create_story_table_in_db
)
from default_story_data import create_default_story_data

def import_story_from_json(file_path: str, story_id: str = None, overwrite: bool = False) -> bool:
    """從 JSON 檔案匯入故事"""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            story_data = json.load(f)
        
        # 取得故事資訊
        if story_id:
            # 使用指定的 story_id
            story_info = {
                'story_id': story_id,
                'title': story_data.get('title', f'匯入的故事 - {story_id}'),
                'description': story_data.get('description', ''),
                'author': story_data.get('author', ''),
                'chapters': story_data.get('chapters', [])
            }
        else:
            # 使用檔案中的資訊
            story_info = {
                'story_id': story_data.get('story_id', Path(file_path).stem),
                'title': story_data.get('title', '未命名故事'),
                'description': story_data.get('description', ''),
                'author': story_data.get('author', ''),
                'chapters': story_data.get('chapters', [])
            }
        
        # 檢查故事是否已存在
        existing_story = get_story_info(story_info['story_id'])
        if existing_story and not overwrite:
            print(f"❌ 故事 '{story_info['story_id']}' 已存在，使用 --overwrite 參數強制覆蓋")
            return False
        
        # 註冊或更新故事
        if existing_story and overwrite:
            print(f"🔄 覆蓋現有故事: {story_info['story_id']}")
            # 清空現有章節
            db = SessionLocal()
            try:
                table_name = f"story_{story_info['story_id']}"
                db.execute(text(f"DELETE FROM {table_name}"))
                db.commit()
            finally:
                db.close()
        else:
            # 註冊新故事
            success = register_story(
                story_id=story_info['story_id'],
                title=story_info['title'],
                description=story_info['description'],
                author=story_info['author']
            )
            if not success:
                print(f"❌ 註冊故事失敗: {story_info['story_id']}")
                return False
        
        # 匯入章節資料
        db = SessionLocal()
        try:
            table_name = f"story_{story_info['story_id']}"
            imported_count = 0
            
            for chapter in story_info['chapters']:
                insert_sql = text(f"""
                    INSERT INTO {table_name} (id, title, content, options)
                    VALUES (:id, :title, :content, :options)
                """)
                
                db.execute(insert_sql, {
                    'id': chapter['id'],
                    'title': chapter['title'],
                    'content': chapter['content'],
                    'options': json.dumps(chapter.get('options', []), ensure_ascii=False)
                })
                imported_count += 1
            
            db.commit()
            print(f"✅ 成功匯入故事 '{story_info['title']}' ({story_info['story_id']})")
            print(f"   匯入章節數: {imported_count}")
            return True
            
        except Exception as e:
            db.rollback()
            print(f"❌ 匯入章節失敗: {e}")
            return False
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ 讀取檔案失敗: {e}")
        return False

def export_story_to_json(story_id: str, output_file: str = None) -> bool:
    """匯出故事到 JSON 檔案"""
    
    try:
        # 取得故事資訊
        story = get_story_info(story_id)
        if not story:
            print(f"❌ 故事不存在: {story_id}")
            return False
        
        # 查詢章節資料
        db = SessionLocal()
        try:
            table_name = story.table_name
            result = db.execute(text(f"SELECT * FROM {table_name} ORDER BY id"))
            chapters = result.fetchall()
            
            # 建立匯出資料
            export_data = {
                "story_id": story.story_id,
                "title": story.title,
                "description": story.description,
                "author": story.author,
                "version": story.version,
                "exported_at": datetime.now().isoformat(),
                "chapters": []
            }
            
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
                export_data["chapters"].append(chapter_data)
            
            # 決定輸出檔案名稱
            if not output_file:
                output_file = f"{story_id}_exported_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # 寫入檔案
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 成功匯出故事到: {output_file}")
            print(f"   故事標題: {story.title}")
            print(f"   章節數量: {len(export_data['chapters'])}")
            return True
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ 匯出失敗: {e}")
        return False

def export_all_stories_to_json(output_file: str = None) -> bool:
    """匯出所有故事到單一 JSON 檔案"""
    
    try:
        db = SessionLocal()
        try:
            # 取得所有故事
            stories = db.query(StoryRegistry).filter(StoryRegistry.is_active == "true").all()
            
            if not stories:
                print("❌ 沒有找到任何故事")
                return False
            
            export_data = {
                "exported_at": datetime.now().isoformat(),
                "total_stories": len(stories),
                "stories": []
            }
            
            for story in stories:
                # 查詢章節資料
                result = db.execute(text(f"SELECT * FROM {story.table_name} ORDER BY id"))
                chapters = result.fetchall()
                
                story_data = {
                    "story_id": story.story_id,
                    "title": story.title,
                    "description": story.description,
                    "author": story.author,
                    "version": story.version,
                    "chapters": []
                }
                
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
                    story_data["chapters"].append(chapter_data)
                
                export_data["stories"].append(story_data)
            
            # 決定輸出檔案名稱
            if not output_file:
                output_file = f"all_stories_exported_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # 寫入檔案
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 成功匯出所有故事到: {output_file}")
            print(f"   故事數量: {len(stories)}")
            total_chapters = sum(len(s["chapters"]) for s in export_data["stories"])
            print(f"   總章節數: {total_chapters}")
            return True
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ 匯出失敗: {e}")
        return False

def list_stories():
    """列出所有故事"""
    
    try:
        db = SessionLocal()
        try:
            stories = db.query(StoryRegistry).filter(StoryRegistry.is_active == "true").all()
            
            if not stories:
                print("📚 沒有找到任何故事")
                return
            
            print(f"📚 找到 {len(stories)} 個故事:")
            print("-" * 80)
            
            for story in stories:
                # 計算章節數量
                result = db.execute(text(f"SELECT COUNT(*) as count FROM {story.table_name}"))
                chapter_count = result.fetchone().count
                
                print(f"🎭 {story.title}")
                print(f"   ID: {story.story_id}")
                print(f"   作者: {story.author or '未知'}")
                print(f"   描述: {story.description or '無描述'}")
                print(f"   章節數: {chapter_count}")
                print(f"   建立時間: {story.created_at}")
                print("-" * 80)
                
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ 列出故事失敗: {e}")

def list_chapters(story_id: str):
    """列出指定故事的所有章節"""
    
    try:
        # 驗證故事存在
        story = get_story_info(story_id)
        if not story:
            print(f"❌ 故事不存在: {story_id}")
            return
        
        db = SessionLocal()
        try:
            result = db.execute(text(f"SELECT * FROM {story.table_name} ORDER BY id"))
            chapters = result.fetchall()
            
            print(f"📖 故事 '{story.title}' 的章節列表:")
            print("-" * 80)
            
            for chapter in chapters:
                options = json.loads(chapter.options) if chapter.options else []
                print(f"第 {chapter.id} 章: {chapter.title}")
                print(f"   內容長度: {len(chapter.content)} 字元")
                print(f"   選項數量: {len(options)}")
                if options:
                    for i, option in enumerate(options, 1):
                        next_id = option.get('next_id', '無')
                        print(f"     {i}. {option['text']} → 第 {next_id} 章")
                print("-" * 80)
                
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ 列出章節失敗: {e}")

def clear_story(story_id: str):
    """清除指定故事的所有資料"""
    
    try:
        # 驗證故事存在
        story = get_story_info(story_id)
        if not story:
            print(f"❌ 故事不存在: {story_id}")
            return
        
        # 確認操作
        response = input(f"⚠️  確定要刪除故事 '{story.title}' ({story_id}) 嗎？(y/N): ")
        if response.lower() != 'y':
            print("❌ 操作已取消")
            return
        
        db = SessionLocal()
        try:
            # 刪除章節資料
            db.execute(text(f"DROP TABLE IF EXISTS {story.table_name}"))
            
            # 刪除註冊記錄
            db.query(StoryRegistry).filter(StoryRegistry.story_id == story_id).delete()
            
            db.commit()
            print(f"✅ 成功刪除故事: {story.title}")
            
        except Exception as e:
            db.rollback()
            print(f"❌ 刪除失敗: {e}")
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ 清除故事失敗: {e}")

def clear_all_stories():
    """清除所有故事資料"""
    
    try:
        # 確認操作
        response = input("⚠️  確定要刪除所有故事嗎？這個操作無法復原！(y/N): ")
        if response.lower() != 'y':
            print("❌ 操作已取消")
            return
        
        db = SessionLocal()
        try:
            # 取得所有故事
            stories = db.query(StoryRegistry).all()
            
            deleted_count = 0
            for story in stories:
                # 刪除故事表格
                db.execute(text(f"DROP TABLE IF EXISTS {story.table_name}"))
                deleted_count += 1
            
            # 清空註冊表
            db.query(StoryRegistry).delete()
            
            db.commit()
            print(f"✅ 成功刪除 {deleted_count} 個故事")
            
        except Exception as e:
            db.rollback()
            print(f"❌ 清除失敗: {e}")
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ 清除所有故事失敗: {e}")

def create_default_story():
    """建立預設故事"""
    
    story_id = "forest_adventure"
    
    # 檢查是否已存在
    existing_story = get_story_info(story_id)
    if existing_story:
        print(f"ℹ️  預設故事 '{story_id}' 已存在")
        return
    
    # 註冊故事
    success = register_story(
        story_id=story_id,
        title="森林冒險",
        description="一個關於勇氣與智慧的森林探險故事，包含豐富的遊戲狀態變數和條件內容",
        author="Story Engine Team"
    )
    
    if not success:
        print(f"❌ 建立預設故事失敗")
        return
    
    # 匯入章節資料
    chapters_data = create_default_story_data()
    
    db = SessionLocal()
    try:
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
        print(f"✅ 成功建立預設故事 '森林冒險'")
        print(f"   匯入章節數: {imported_count}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 匯入預設故事失敗: {e}")
    finally:
        db.close()

def main():
    """主要執行函數"""
    
    parser = argparse.ArgumentParser(
        description="Story Engine API - 故事資料管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用範例:
  python seed_data.py                                    # 建立預設故事
  python seed_data.py --list-stories                     # 列出所有故事
  python seed_data.py --list-chapters forest_adventure   # 列出指定故事的章節
  python seed_data.py --import-story story.json          # 匯入故事
  python seed_data.py --export-story forest_adventure    # 匯出指定故事
  python seed_data.py --export-all-stories               # 匯出所有故事
  python seed_data.py --clear-story forest_adventure     # 刪除指定故事
  python seed_data.py --clear-all                        # 刪除所有故事
        """
    )
    
    parser.add_argument('--list-stories', action='store_true', help='列出所有故事')
    parser.add_argument('--list-chapters', metavar='STORY_ID', help='列出指定故事的章節')
    parser.add_argument('--import-story', metavar='JSON_FILE', help='從 JSON 檔案匯入故事')
    parser.add_argument('--story-id', metavar='ID', help='指定匯入故事的 ID（可選）')
    parser.add_argument('--overwrite', action='store_true', help='覆蓋現有故事')
    parser.add_argument('--export-story', metavar='STORY_ID', help='匯出指定故事到 JSON 檔案')
    parser.add_argument('--export-all-stories', action='store_true', help='匯出所有故事到單一 JSON 檔案')
    parser.add_argument('--output', metavar='FILE', help='指定輸出檔案名稱')
    parser.add_argument('--clear-story', metavar='STORY_ID', help='刪除指定故事')
    parser.add_argument('--clear-all', action='store_true', help='刪除所有故事')
    
    args = parser.parse_args()
    
    # 初始化資料庫
    create_tables()
    
    try:
        if args.list_stories:
            list_stories()
        elif args.list_chapters:
            list_chapters(args.list_chapters)
        elif args.import_story:
            import_story_from_json(args.import_story, args.story_id, args.overwrite)
        elif args.export_story:
            export_story_to_json(args.export_story, args.output)
        elif args.export_all_stories:
            export_all_stories_to_json(args.output)
        elif args.clear_story:
            clear_story(args.clear_story)
        elif args.clear_all:
            clear_all_stories()
        else:
            # 預設行為：建立預設故事
            create_default_story()
            
    except KeyboardInterrupt:
        print("\n⚠️  操作被使用者中斷")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 執行失敗: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
