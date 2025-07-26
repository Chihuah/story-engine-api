"""
故事資料管理工具
支援匯入、匯出、清除故事章節資料
"""

import json
import os
import argparse
from sqlalchemy.orm import Session
from models import SessionLocal, Chapter, create_tables

def create_default_story_data():
    """建立預設故事章節資料"""
    
    chapters_data = [
        {
            "id": 1,
            "title": "森林入口",
            "content": """你站在一片古老森林的入口處。陽光透過樹葉灑下斑駁的光影，遠處傳來鳥兒的啁啾聲。一條小徑蜿蜒向前，消失在樹林深處。

你注意到路邊有一個破舊的木牌，上面刻著模糊的文字：「小心...野獸...」

你要如何行動？""",
            "options": [
                {
                    "text": "沿著小徑深入森林",
                    "next_id": 2
                },
                {
                    "text": "在入口處仔細觀察周圍環境",
                    "next_id": 3
                }
            ]
        },
        {
            "id": 2,
            "title": "森林深處",
            "content": """你沿著小徑走了約十分鐘，森林變得越來越茂密。突然，你聽到前方傳來奇怪的聲音——像是某種大型動物的低吼。

[[IF has_weapon]]
你握緊手中的武器，感到稍微安心一些。
[[ENDIF]]

樹叢中似乎有什麼東西在移動。你的心跳加速，必須做出決定。""",
            "options": [
                {
                    "text": "小心翼翼地靠近聲音來源",
                    "next_id": 4
                },
                {
                    "text": "立即轉身逃跑",
                    "next_id": 5
                }
            ]
        },
        {
            "id": 3,
            "title": "發現線索",
            "content": """你仔細觀察周圍，在木牌附近的草叢中發現了一根粗糙的木棍。雖然不是什麼好武器，但總比空手好。

你撿起木棍，感覺稍微有了一些安全感。繼續觀察，你還注意到地面上有一些不尋常的腳印——比人類的腳印大得多，而且有爪痕。

現在你對前方的危險有了更多了解。""",
            "options": [
                {
                    "text": "帶著木棍進入森林",
                    "next_id": 6
                },
                {
                    "text": "決定不冒險，離開這裡",
                    "next_id": 7
                }
            ]
        },
        {
            "id": 4,
            "title": "遭遇野獸（結局一：勇敢面對）",
            "content": """你小心地撥開樹叢，看到一隻巨大的棕熊正在覓食。牠注意到了你的存在，站起身來，發出威脅性的咆哮。

[[IF has_weapon]]
你舉起手中的武器，雖然只是一根木棍，但你的勇氣讓棕熊感到猶豫。經過一番對峙，棕熊最終選擇離開，消失在森林深處。

你成功地通過了這次考驗，證明了勇氣有時比武器更重要。
[[ELSE]]
沒有武器的你只能依靠勇氣。你大聲喊叫並揮舞雙臂，試圖嚇退棕熊。令人驚訝的是，你的勇敢行為奏效了！棕熊被你的氣勢震懾，緩緩退入森林深處。

你證明了有時候勇氣比任何武器都更有效。
[[ENDIF]]

**遊戲結束 - 勇敢的冒險者**""",
            "options": []
        },
        {
            "id": 5,
            "title": "逃跑（結局二：明智的撤退）",
            "content": """你決定不冒不必要的風險，迅速轉身沿著小徑跑回森林入口。身後傳來的咆哮聲證實了你的判斷是正確的。

回到安全的地方，你意識到有時候撤退是最明智的選擇。森林中確實有危險的野獸，但你活著離開了，這本身就是一種勝利。

你學會了在面對未知危險時，謹慎和智慧同樣重要。

**遊戲結束 - 明智的生存者**""",
            "options": []
        },
        {
            "id": 6,
            "title": "有備而來（結局三：準備充分的勝利）",
            "content": """帶著木棍，你自信地進入森林。由於事先的觀察和準備，你對可能遇到的危險有了心理準備。

當你遇到那隻棕熊時，你沒有驚慌。你冷靜地舉起木棍，保持距離，並緩慢後退。你的準備和冷靜讓你成功地避免了衝突。

棕熊看到你有武器且態度堅定，選擇了離開。你繼續探索森林，發現了一個美麗的瀑布和一些珍貴的藥草。

你的謹慎準備讓這次冒險既安全又有收穫。

**遊戲結束 - 準備充分的探險家**""",
            "options": []
        },
        {
            "id": 7,
            "title": "安全第一（結局四：謹慎的選擇）",
            "content": """看到那些巨大的腳印和爪痕，你決定這次冒險的風險太大了。雖然森林中可能有寶藏或美景，但你的生命更寶貴。

你轉身離開森林，回到了熟悉的村莊。雖然沒有獲得什麼冒險的收穫，但你安全地回到了家。

有時候，知道何時停止比知道何時前進更重要。你選擇了安全，這也是一種智慧。

**遊戲結束 - 謹慎的智者**""",
            "options": []
        }
    ]
    
    return chapters_data

def load_story_from_json(file_path):
    """從 JSON 檔案載入故事資料"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 驗證資料格式
        if not isinstance(data, list):
            raise ValueError("JSON 檔案必須包含章節陣列")
        
        for chapter in data:
            required_fields = ['id', 'title', 'content', 'options']
            for field in required_fields:
                if field not in chapter:
                    raise ValueError(f"章節缺少必要欄位: {field}")
        
        print(f"✅ 成功載入 {len(data)} 個章節從 {file_path}")
        return data
        
    except FileNotFoundError:
        print(f"❌ 找不到檔案: {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ JSON 格式錯誤: {e}")
        return None
    except ValueError as e:
        print(f"❌ 資料格式錯誤: {e}")
        return None

def export_story_to_json(file_path, chapters_data=None):
    """匯出故事資料為 JSON 檔案"""
    if chapters_data is None:
        chapters_data = create_default_story_data()
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(chapters_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 故事資料已匯出至 {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ 匯出失敗: {e}")
        return False

def import_chapters_to_database(chapters_data):
    """匯入章節資料到資料庫"""
    
    # 建立資料表
    create_tables()
    
    # 取得資料庫 Session
    db = SessionLocal()
    
    try:
        # 匯入章節資料
        imported_count = 0
        for chapter_data in chapters_data:
            # 檢查章節是否已存在
            existing_chapter = db.query(Chapter).filter(Chapter.id == chapter_data["id"]).first()
            
            if existing_chapter:
                # 更新現有章節
                existing_chapter.title = chapter_data["title"]
                existing_chapter.content = chapter_data["content"]
                existing_chapter.options = json.dumps(chapter_data["options"], ensure_ascii=False)
                print(f"🔄 更新章節 {existing_chapter.id}: {existing_chapter.title}")
            else:
                # 新增章節
                options_json = json.dumps(chapter_data["options"], ensure_ascii=False)
                
                chapter = Chapter(
                    id=chapter_data["id"],
                    title=chapter_data["title"],
                    content=chapter_data["content"],
                    options=options_json
                )
                
                db.add(chapter)
                print(f"➕ 新增章節 {chapter.id}: {chapter.title}")
            
            imported_count += 1
        
        # 提交變更
        db.commit()
        print(f"✅ 成功匯入 {imported_count} 個章節")
        
        # 驗證資料
        total_chapters = db.query(Chapter).count()
        print(f"📊 資料庫中共有 {total_chapters} 個章節")
        
        return True
        
    except Exception as e:
        print(f"❌ 匯入資料時發生錯誤: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def export_database_to_json(file_path):
    """從資料庫匯出故事資料為 JSON 檔案"""
    
    db = SessionLocal()
    
    try:
        # 查詢所有章節
        chapters = db.query(Chapter).order_by(Chapter.id).all()
        
        if not chapters:
            print("⚠️  資料庫中沒有章節資料")
            return False
        
        # 轉換為 JSON 格式
        chapters_data = []
        for chapter in chapters:
            options = []
            if chapter.options:
                try:
                    options = json.loads(chapter.options)
                except json.JSONDecodeError:
                    print(f"⚠️  章節 {chapter.id} 的選項格式有誤")
                    options = []
            
            chapter_data = {
                "id": chapter.id,
                "title": chapter.title,
                "content": chapter.content,
                "options": options
            }
            chapters_data.append(chapter_data)
        
        # 匯出到檔案
        return export_story_to_json(file_path, chapters_data)
        
    except Exception as e:
        print(f"❌ 匯出資料時發生錯誤: {e}")
        return False
    finally:
        db.close()

def clear_database():
    """清除資料庫中的所有章節"""
    
    db = SessionLocal()
    
    try:
        # 查詢章節數量
        count = db.query(Chapter).count()
        
        if count == 0:
            print("ℹ️  資料庫已經是空的")
            return True
        
        # 清除所有章節
        db.query(Chapter).delete()
        db.commit()
        
        print(f"🗑️  已清除 {count} 個章節")
        return True
        
    except Exception as e:
        print(f"❌ 清除資料時發生錯誤: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def list_chapters():
    """列出資料庫中的所有章節"""
    
    db = SessionLocal()
    
    try:
        chapters = db.query(Chapter).order_by(Chapter.id).all()
        
        if not chapters:
            print("ℹ️  資料庫中沒有章節資料")
            return
        
        print(f"📚 資料庫中的章節列表 (共 {len(chapters)} 個):")
        print("-" * 60)
        
        for chapter in chapters:
            options_count = 0
            if chapter.options:
                try:
                    options = json.loads(chapter.options)
                    options_count = len(options)
                except json.JSONDecodeError:
                    pass
            
            status = "結局" if options_count == 0 else f"{options_count} 個選項"
            print(f"第 {chapter.id:2d} 章: {chapter.title:<20} ({status})")
        
    except Exception as e:
        print(f"❌ 查詢資料時發生錯誤: {e}")
    finally:
        db.close()

def main():
    """主程式"""
    parser = argparse.ArgumentParser(
        description="故事資料管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用範例:
  python seed_data.py                          # 載入預設故事資料
  python seed_data.py --import story.json      # 從 JSON 檔案匯入故事
  python seed_data.py --export story.json      # 匯出故事到 JSON 檔案
  python seed_data.py --clear                  # 清除所有章節
  python seed_data.py --list                   # 列出所有章節
  python seed_data.py --export-db story.json   # 從資料庫匯出到 JSON
        """
    )
    
    parser.add_argument(
        '--import', 
        dest='import_file',
        help='從 JSON 檔案匯入故事資料'
    )
    
    parser.add_argument(
        '--export',
        dest='export_file',
        help='匯出預設故事資料到 JSON 檔案'
    )
    
    parser.add_argument(
        '--export-db',
        dest='export_db_file',
        help='從資料庫匯出故事資料到 JSON 檔案'
    )
    
    parser.add_argument(
        '--clear',
        action='store_true',
        help='清除資料庫中的所有章節'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='列出資料庫中的所有章節'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("📖 故事資料管理工具")
    print("=" * 60)
    
    # 處理命令列參數
    if args.import_file:
        # 從 JSON 檔案匯入
        chapters_data = load_story_from_json(args.import_file)
        if chapters_data:
            import_chapters_to_database(chapters_data)
    
    elif args.export_file:
        # 匯出預設故事到 JSON 檔案
        export_story_to_json(args.export_file)
    
    elif args.export_db_file:
        # 從資料庫匯出到 JSON 檔案
        export_database_to_json(args.export_db_file)
    
    elif args.clear:
        # 清除資料庫
        confirm = input("⚠️  確定要清除所有章節嗎？(y/N): ")
        if confirm.lower() in ['y', 'yes']:
            clear_database()
        else:
            print("❌ 取消操作")
    
    elif args.list:
        # 列出章節
        list_chapters()
    
    else:
        # 預設行為：載入預設故事資料
        print("🚀 載入預設故事資料...")
        chapters_data = create_default_story_data()
        if import_chapters_to_database(chapters_data):
            # 同時匯出 JSON 檔案
            export_story_to_json("story_data.json", chapters_data)
    
    print("=" * 60)
    print("✨ 操作完成")

if __name__ == "__main__":
    main()

