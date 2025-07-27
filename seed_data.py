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

def create_default_story_data():
    """建立預設故事章節資料（增強森林冒險 - 包含數值比較系統）"""
    
    chapters_data = [
        {
            "id": 1,
            "title": "森林入口",
            "content": """你站在一片古老森林的邊緣，高大的樹木遮天蔽日，神秘的霧氣在林間飄蕩。

你是一名經驗豐富的冒險者，當前狀態：
[[IF health >= 80]]你感覺身體健康，精力充沛。[[ENDIF]]
[[IF health < 80]]你感覺有些疲憊，需要小心行事。[[ENDIF]]
[[IF strength >= 15]]你的肌肉結實有力，能夠應對大部分挑戰。[[ENDIF]]
[[IF wisdom >= 12]]你的頭腦清晰敏銳，善於分析情況。[[ENDIF]]

傳說這片森林中隱藏著古老的寶藏，但也充滿了未知的危險。你背著簡單的行囊，心中既興奮又緊張。

在你面前有兩條小徑：一條看起來較為平坦，另一條則蜿蜒向森林深處。""",
            "options": [
                {"text": "選擇平坦的小徑", "next_id": 2, "game_state": {"took_risk": False, "played_safe": True}},
                {"text": "選擇蜿蜒的小徑", "next_id": 3, "game_state": {"took_risk": True, "played_safe": False}}
            ]
        },
        {
            "id": 2,
            "title": "森林深處",
            "content": """你選擇了看似安全的平坦小徑，但很快就發現這條路並不如想像中簡單。

[[IF played_safe]]你謹慎的個性讓你時刻保持警覺。[[ENDIF]]
[[IF health > 70]]你的良好體力讓你能夠輕鬆應對路上的小障礙。[[ENDIF]]
[[IF health <= 70]]你感到有些吃力，每一步都需要小心。[[ENDIF]]

前方傳來奇怪的聲音，像是某種大型動物的咆哮。你停下腳步，仔細聆聽。

[[IF has_weapon]]你握緊手中的武器，準備應對可能的危險。[[ENDIF]]
[[IF NOT has_weapon]]你意識到自己手無寸鐵，心中有些緊張。[[ENDIF]]
[[IF strength >= 18]]你感覺自己有足夠的力量面對大部分威脅。[[ENDIF]]
[[IF strength < 18]]你意識到可能需要依靠智慧而非蠻力。[[ENDIF]]""",
            "options": [
                {"text": "勇敢地繼續前進", "next_id": 4, "game_state": {"showed_courage": True}},
                {"text": "小心翼翼地繞道而行", "next_id": 5, "game_state": {"cautious": True}}
            ]
        },
        {
            "id": 3,
            "title": "發現線索",
            "content": """蜿蜒的小徑帶你來到一個小空地，這裡有一口古老的井。

[[IF took_risk]]你的冒險精神得到了回報。[[ENDIF]]

井邊刻著古老的符文，井水清澈見底，散發著淡淡的藍光。在井旁的石頭上，你發現了一把生鏽的短劍和一張破舊的地圖。

[[IF drank_water]]魔法井水的效果讓你感到精神煥發。[[ENDIF]]
[[IF wisdom >= 15]]你能夠部分理解符文的含義，它們似乎在警告什麼。[[ENDIF]]
[[IF wisdom < 15]]符文對你來說完全是謎團。[[ENDIF]]""",
            "options": [
                {"text": "喝一口井水", "next_id": 6, "game_state": {"drank_water": True, "magic_enhanced": True, "health": 20, "wisdom": 3}},
                {"text": "拿起短劍和地圖", "next_id": 7, "game_state": {"has_weapon": True, "has_map": True, "strength": 2}},
                {"text": "仔細研究符文", "next_id": 8, "game_state": {"gained_wisdom": True, "wisdom": 5}}
            ]
        },
        {
            "id": 4,
            "title": "遭遇野獸",
            "content": """你勇敢地繼續前進，很快就遇到了聲音的來源——一隻巨大的森林熊！

[[IF showed_courage]]你的勇氣讓你在面對危險時保持冷靜。[[ENDIF]]
[[IF has_weapon]]幸好你有武器在手！[[ENDIF]]
[[IF magic_enhanced]]魔法的力量在你體內流淌，給了你額外的信心。[[ENDIF]]
[[IF strength >= 20]]你感覺自己有足夠的力量與熊正面對抗。[[ENDIF]]
[[IF strength < 20]]你意識到正面對抗可能不是明智的選擇。[[ENDIF]]

熊看起來很餓，正在尋找食物。你必須做出選擇。

[[IF health <= 50]]你的體力不足，戰鬥會很危險。[[ENDIF]]
[[IF wisdom >= 18]]你的智慧讓你想到了幾種不同的應對策略。[[ENDIF]]""",
            "options": [
                {"text": "與熊戰鬥（需要力量 ≥ 18）", "next_id": 12, "game_state": {"faced_guardian": True, "health": -25}, "condition": "strength >= 18"},
                {"text": "嘗試與熊溝通（需要智慧 ≥ 15）", "next_id": 13, "game_state": {"showed_wisdom": True, "wisdom": 3}, "condition": "wisdom >= 15"},
                {"text": "慢慢後退", "next_id": 14, "game_state": {"cautious": True, "health": -5, "courage": -1}}
            ]
        },
        {
            "id": 5,
            "title": "逃跑",
            "content": """你決定謹慎行事，繞道而行。這個決定讓你避開了危險，但也錯過了一些機會。

[[IF cautious]]你的謹慎個性再次發揮了作用。[[ENDIF]]
[[IF health < 60]]你的體力不足，繞道是明智的選擇。[[ENDIF]]

在繞道的過程中，你發現了一條隱蔽的小徑，似乎通向森林的另一個區域。

[[IF has_map]]地圖上顯示這條小徑可能通向寶藏所在地。[[ENDIF]]
[[IF wisdom >= 12]]你的智慧讓你意識到這條小徑可能很重要。[[ENDIF]]""",
            "options": [
                {"text": "跟隨隱蔽小徑", "next_id": 15, "game_state": {"found_hidden_path": True}},
                {"text": "返回主要道路", "next_id": 16, "game_state": {"played_safe": True}}
            ]
        },
        {
            "id": 6,
            "title": "魔法增強",
            "content": """你小心地喝了一口井水，立刻感到一股暖流遍布全身。

[[IF drank_water]]井水的味道甘甜，帶有淡淡的魔法氣息。[[ENDIF]]
[[IF magic_enhanced]]你感到力量、智慧和敏捷都得到了提升。[[ENDIF]]
[[IF health >= 90]]你現在感覺前所未有的強壯。[[ENDIF]]
[[IF wisdom >= 15]]增強的智慧讓你能夠更好地理解周圍的魔法能量。[[ENDIF]]

這口井顯然有著神奇的力量。你現在感覺比以往任何時候都要強大。

在井底，你還看到了一枚閃閃發光的金幣。""",
            "options": [
                {"text": "取出金幣", "next_id": 17, "game_state": {"has_gold": True}},
                {"text": "離開這裡繼續探索", "next_id": 18, "game_state": {"respectful": True, "wisdom": 2}}
            ]
        },
        {
            "id": 12,
            "title": "勇敢戰鬥",
            "content": """你決定與森林熊戰鬥！

[[IF faced_guardian]]戰鬥激烈而危險。[[ENDIF]]
[[IF strength >= 25]]你的強大力量讓你在戰鬥中佔據上風。[[ENDIF]]
[[IF health <= 30]]戰鬥讓你受了重傷，你感到頭暈目眩。[[ENDIF]]
[[IF health <= 0]]你的傷勢過重，意識開始模糊...遊戲結束。[[ENDIF]]

[[IF health > 0]]經過激烈的戰鬥，你終於擊敗了洞穴熊。在熊的巢穴深處，你發現了一把古老的劍和一瓶治療藥水。

雖然受了傷，但你成功地完成了這次冒險。你的勇氣將被森林中的生物們銘記。[[ENDIF]]""",
            "options": [
                {"text": "使用治療藥水（如果生命值 > 0）", "next_id": 19, "game_state": {"used_potion": True, "health": 40, "has_ancient_sword": True}, "condition": "health > 0"},
                {"text": "保存藥水，拿起古劍（如果生命值 > 0）", "next_id": 20, "game_state": {"saved_potion": True, "has_healing_potion": True, "has_ancient_sword": True, "strength": 5}, "condition": "health > 0"}
            ]
        },
        {
            "id": 13,
            "title": "智慧溝通",
            "content": """你決定用智慧來解決這個問題。

[[IF showed_wisdom]]你的聰明才智派上了用場。[[ENDIF]]
[[IF wisdom >= 20]]你的高智慧讓你想出了完美的解決方案。[[ENDIF]]

你注意到熊的行為模式，發現它只是在保護自己的幼崽。你慢慢後退，並用手勢表示自己沒有惡意。

熊逐漸放鬆警惕，甚至帶你到了一個隱秘的寶藏室。作為對你智慧的獎勵，熊允許你拿走一件寶物。

[[IF wisdom >= 25]]你的超凡智慧讓熊對你產生了深深的敬意。[[ENDIF]]""",
            "options": [
                {"text": "選擇智慧之書", "next_id": 21, "game_state": {"has_wisdom_book": True, "wisdom": 10, "bear_friend": True}},
                {"text": "選擇力量護符", "next_id": 22, "game_state": {"has_strength_amulet": True, "strength": 8, "bear_friend": True}}
            ]
        },
        {
            "id": 19,
            "title": "恢復活力",
            "content": """你喝下了治療藥水，感到傷口迅速癒合。

[[IF used_potion]]藥水的效果非常顯著。[[ENDIF]]
[[IF health >= 60]]你現在感覺好多了，可以繼續冒險。[[ENDIF]]
[[IF has_ancient_sword]]古劍在你手中散發著神秘的光芒。[[ENDIF]]
[[IF strength >= 20]]結合你的力量，這把古劍將成為強大的武器。[[ENDIF]]

現在你必須決定下一步的行動。森林深處似乎還有更多的秘密等待發現。

[[IF health >= 80]]你的體力已經完全恢復，感覺比以前更強壯。[[ENDIF]]""",
            "options": [
                {"text": "探索森林深處（需要生命值 ≥ 70）", "next_id": 23, "game_state": {"explored_deep": True}, "condition": "health >= 70"},
                {"text": "返回村莊", "next_id": 24, "game_state": {"returned_home": True}}
            ]
        },
        {
            "id": 21,
            "title": "智慧的極致",
            "content": """你選擇了智慧之書，這是一個明智的決定。

[[IF has_wisdom_book]]古老的知識湧入你的腦海。[[ENDIF]]
[[IF bear_friend]]熊成為了你的朋友和守護者。[[ENDIF]]
[[IF wisdom >= 30]]你現在擁有了接近聖賢的智慧。[[ENDIF]]

書中記載著古老的魔法和森林的秘密。你學會了與自然溝通的方法，以及一些強大的治療和保護法術。

[[IF wisdom >= 35]]你的智慧已經超越了常人的理解範圍。[[ENDIF]]

你成為了森林的智者，所有的生物都尊敬你。你的智慧將指引未來的冒險者。""",
            "options": []
        },
        {
            "id": 23,
            "title": "森林的心臟",
            "content": """你深入森林，來到了一個神秘的聖地。

[[IF explored_deep]]你的勇氣和決心讓你發現了這個秘密。[[ENDIF]]
[[IF has_ancient_sword]]古劍與聖地產生了共鳴。[[ENDIF]]
[[IF health >= 90]]你的完美狀態讓你能夠承受聖地的神秘力量。[[ENDIF]]
[[IF wisdom >= 20]]你的智慧讓你理解了這個地方的真正意義。[[ENDIF]]

在聖地的中央，有一個古老的祭壇。祭壇上放著三個神秘的寶珠，每個都散發著不同的能量。

[[IF strength >= 25]]你感覺到紅色寶珠與你的力量產生共鳴。[[ENDIF]]
[[IF wisdom >= 25]]藍色寶珠似乎在呼喚你的智慧。[[ENDIF]]
[[IF health >= 90]]綠色寶珠散發著生命的氣息。[[ENDIF]]""",
            "options": [
                {"text": "選擇力量寶珠（需要力量 ≥ 20）", "next_id": 25, "game_state": {"chose_power": True, "strength": 15}, "condition": "strength >= 20"},
                {"text": "選擇智慧寶珠（需要智慧 ≥ 20）", "next_id": 26, "game_state": {"chose_wisdom": True, "wisdom": 15}, "condition": "wisdom >= 20"},
                {"text": "選擇生命寶珠（需要生命值 ≥ 80）", "next_id": 27, "game_state": {"chose_life": True, "health": 50}, "condition": "health >= 80"}
            ]
        },
        {
            "id": 25,
            "title": "力量的傳說",
            "content": """你選擇了力量寶珠，感受到無窮的力量湧入身體。

[[IF chose_power]]你現在擁有了傳說級的力量。[[ENDIF]]
[[IF strength >= 35]]你的力量已經超越了人類的極限。[[ENDIF]]

突然，森林中出現了一道巨大的石門，阻擋著通往最終寶藏的道路。只有擁有足夠力量的人才能推開它。

[[IF strength >= 40]]你感覺自己絕對有能力推開這道門。[[ENDIF]]

你運用全身的力量，成功推開了傳說中的力量之門！門後是無盡的寶藏和榮耀。

你成為了力量的化身，你的傳說將永遠流傳下去！""",
            "options": []
        },
        {
            "id": 26,
            "title": "智慧的啟示",
            "content": """你選擇了智慧寶珠，感受到無盡的知識湧入腦海。

[[IF chose_wisdom]]你現在擁有了近乎全知的智慧。[[ENDIF]]
[[IF wisdom >= 35]]你的智慧已經達到了神明的層次。[[ENDIF]]

你突然理解了宇宙的奧秘，森林的所有秘密都向你敞開。你學會了控制自然的力量，能夠與所有生物溝通。

[[IF wisdom >= 40]]你的智慧讓你看透了時間和空間的本質。[[ENDIF]]

你成為了森林的守護者和智慧的象徵。所有尋求知識的人都會來向你請教。

你的智慧將指引世界走向更美好的未來！""",
            "options": []
        },
        {
            "id": 27,
            "title": "生命的永恆",
            "content": """你選擇了生命寶珠，感受到無盡的生命力湧入身體。

[[IF chose_life]]你現在擁有了近乎不朽的生命力。[[ENDIF]]
[[IF health >= 130]]你的生命力已經超越了凡人的極限。[[ENDIF]]

你的身體變得完美無瑕，所有的傷痛都消失了。你獲得了治療他人的能力，成為了生命的守護者。

[[IF health >= 150]]你的生命力如此強大，甚至能夠復活死者。[[ENDIF]]

森林中的所有生物都感受到了你的生命能量，它們向你表示敬意。你成為了生命的化身。

你將用你的力量治癒世界，帶來和平與繁榮！""",
            "options": []
        }
    ]
    
    return chapters_data

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
                chapter_data = {
                    "id": chapter.id,
                    "title": chapter.title,
                    "content": chapter.content,
                    "options": json.loads(chapter.options) if chapter.options else []
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
                    chapter_data = {
                        "id": chapter.id,
                        "title": chapter.title,
                        "content": chapter.content,
                        "options": json.loads(chapter.options) if chapter.options else []
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
