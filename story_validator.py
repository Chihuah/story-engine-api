#!/usr/bin/env python3
"""
故事檔案驗證工具
檢查故事檔案的完整性、邏輯和格式
支援新的多資料表架構和故事檔案格式
"""

import json
import argparse
import re
import sys
from typing import List, Dict, Set, Any, Optional
from datetime import datetime

class StoryValidator:
    """故事驗證器"""
    
    def __init__(self, verbose: bool = False):
        self.errors = []
        self.warnings = []
        self.story_data = None
        self.story_info = {}
        self.chapters = []
        self.chapter_ids = set()
        self.verbose = verbose
        
    def log(self, message: str):
        """記錄詳細訊息"""
        if self.verbose:
            print(f"🔍 {message}")
    
    def load_story(self, file_path: str) -> bool:
        """載入故事檔案"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.story_data = json.load(f)
            
            # 檢查檔案格式
            if isinstance(self.story_data, list):
                # 舊格式：直接是章節陣列
                self.log("偵測到舊格式故事檔案")
                self.chapters = self.story_data
                self.story_info = {
                    "story_id": "unknown",
                    "title": "未命名故事",
                    "description": "",
                    "author": "",
                    "version": "1.0"
                }
                self.warnings.append("使用舊格式，建議升級為新格式")
                
            elif isinstance(self.story_data, dict):
                # 新格式：包含 story_info 和 chapters
                if "story_info" in self.story_data and "chapters" in self.story_data:
                    self.log("偵測到新格式故事檔案")
                    self.story_info = self.story_data["story_info"]
                    self.chapters = self.story_data["chapters"]
                else:
                    # 可能是單一故事的舊格式
                    if "id" in self.story_data and "title" in self.story_data:
                        self.log("偵測到單章節格式")
                        self.chapters = [self.story_data]
                        self.story_info = {
                            "story_id": "unknown",
                            "title": "未命名故事",
                            "description": "",
                            "author": "",
                            "version": "1.0"
                        }
                    else:
                        self.errors.append("無法識別的故事檔案格式")
                        return False
            else:
                self.errors.append("故事檔案格式錯誤")
                return False
            
            # 收集所有章節 ID
            self.chapter_ids = {chapter.get('id') for chapter in self.chapters if 'id' in chapter}
            
            print(f"✅ 成功載入故事: {self.story_info.get('title', '未命名')}")
            print(f"📚 章節數量: {len(self.chapters)}")
            return True
            
        except FileNotFoundError:
            self.errors.append(f"找不到檔案: {file_path}")
            return False
        except json.JSONDecodeError as e:
            self.errors.append(f"JSON 格式錯誤: {e}")
            return False
        except Exception as e:
            self.errors.append(f"載入檔案時發生錯誤: {e}")
            return False
    
    def validate_story_info(self):
        """驗證故事資訊"""
        print("📖 檢查故事資訊...")
        
        # 必要欄位
        required_fields = ['story_id', 'title']
        for field in required_fields:
            if field not in self.story_info:
                self.errors.append(f"故事資訊缺少必要欄位: {field}")
            elif not self.story_info[field]:
                self.errors.append(f"故事資訊欄位 '{field}' 不能為空")
        
        # 推薦欄位
        recommended_fields = ['description', 'author', 'version']
        for field in recommended_fields:
            if field not in self.story_info or not self.story_info[field]:
                self.warnings.append(f"建議添加故事資訊欄位: {field}")
        
        # 驗證 story_id 格式
        if 'story_id' in self.story_info:
            story_id = self.story_info['story_id']
            if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', story_id):
                self.errors.append("story_id 必須以字母開頭，只能包含字母、數字和底線")
            elif len(story_id) > 50:
                self.errors.append("story_id 長度不能超過 50 個字元")
        
        # 檢查標題長度
        if 'title' in self.story_info:
            title = self.story_info['title']
            if len(title) > 255:
                self.errors.append("故事標題長度不能超過 255 個字元")
            elif len(title) < 3:
                self.warnings.append("故事標題過短，建議至少 3 個字元")
    
    def validate_structure(self):
        """驗證基本結構"""
        print("🔍 檢查基本結構...")
        
        if not self.chapters:
            self.errors.append("故事沒有章節")
            return
        
        required_fields = ['id', 'title', 'content', 'options']
        
        for i, chapter in enumerate(self.chapters):
            chapter_ref = f"章節 {i+1}"
            
            # 檢查必要欄位
            for field in required_fields:
                if field not in chapter:
                    self.errors.append(f"{chapter_ref}: 缺少必要欄位 '{field}'")
                elif field != 'options' and not chapter[field]:  # options 可以是空陣列
                    self.warnings.append(f"{chapter_ref}: 欄位 '{field}' 是空的")
            
            # 檢查 ID 類型和唯一性
            if 'id' in chapter:
                chapter_id = chapter['id']
                if not isinstance(chapter_id, int):
                    self.errors.append(f"{chapter_ref}: ID 必須是整數")
                elif chapter_id <= 0:
                    self.errors.append(f"{chapter_ref}: ID 必須是正整數")
                else:
                    chapter_ref = f"章節 {chapter_id}"
                    # 檢查重複 ID
                    id_count = sum(1 for c in self.chapters if c.get('id') == chapter_id)
                    if id_count > 1:
                        self.errors.append(f"{chapter_ref}: 重複的章節 ID")
            
            # 檢查標題和內容
            if 'title' in chapter:
                if not isinstance(chapter['title'], str):
                    self.errors.append(f"{chapter_ref}: 標題必須是字串")
                elif len(chapter['title']) > 255:
                    self.errors.append(f"{chapter_ref}: 標題長度不能超過 255 個字元")
                elif len(chapter['title']) < 3:
                    self.warnings.append(f"{chapter_ref}: 標題過短")
            
            if 'content' in chapter:
                if not isinstance(chapter['content'], str):
                    self.errors.append(f"{chapter_ref}: 內容必須是字串")
                elif len(chapter['content']) < 10:
                    self.warnings.append(f"{chapter_ref}: 內容過短")
                elif len(chapter['content']) > 10000:
                    self.warnings.append(f"{chapter_ref}: 內容過長，可能影響閱讀體驗")
            
            # 檢查選項格式
            if 'options' in chapter:
                options = chapter['options']
                if not isinstance(options, list):
                    self.errors.append(f"{chapter_ref}: 選項必須是陣列")
                else:
                    if len(options) > 10:
                        self.warnings.append(f"{chapter_ref}: 選項過多 ({len(options)} 個)，可能影響遊戲體驗")
                    
                    for j, option in enumerate(options):
                        option_ref = f"{chapter_ref}, 選項 {j+1}"
                        
                        if not isinstance(option, dict):
                            self.errors.append(f"{option_ref}: 選項必須是物件")
                            continue
                        
                        # 檢查必要欄位
                        if 'text' not in option:
                            self.errors.append(f"{option_ref}: 缺少 'text' 欄位")
                        elif not isinstance(option['text'], str):
                            self.errors.append(f"{option_ref}: 'text' 必須是字串")
                        elif not option['text'].strip():
                            self.errors.append(f"{option_ref}: 選項文字不能為空")
                        
                        if 'next_id' not in option:
                            self.errors.append(f"{option_ref}: 缺少 'next_id' 欄位")
                        elif not isinstance(option['next_id'], int):
                            self.errors.append(f"{option_ref}: 'next_id' 必須是整數")
                        
                        # 檢查遊戲狀態變更
                        if 'game_state' in option:
                            if not isinstance(option['game_state'], dict):
                                self.errors.append(f"{option_ref}: 'game_state' 必須是物件")
    
    def validate_references(self):
        """驗證章節引用"""
        print("🔗 檢查章節引用...")
        
        referenced_ids = set()
        
        for chapter in self.chapters:
            chapter_id = chapter.get('id')
            chapter_ref = f"章節 {chapter_id}" if chapter_id else "未知章節"
            
            if 'options' in chapter:
                for j, option in enumerate(chapter['options']):
                    if 'next_id' in option:
                        next_id = option['next_id']
                        referenced_ids.add(next_id)
                        
                        if next_id not in self.chapter_ids:
                            self.errors.append(f"{chapter_ref}, 選項 {j+1}: 引用不存在的章節 {next_id}")
        
        # 檢查孤立章節（除了起始章節）
        start_chapter_id = 1
        unreferenced_ids = self.chapter_ids - referenced_ids - {start_chapter_id}
        
        for chapter_id in unreferenced_ids:
            self.warnings.append(f"章節 {chapter_id} 沒有被任何選項引用（可能是孤立章節）")
    
    def validate_logic_structure(self):
        """驗證邏輯結構"""
        print("🧠 檢查邏輯結構...")
        
        # 檢查起始章節
        if 1 not in self.chapter_ids:
            self.errors.append("缺少起始章節（ID = 1）")
        
        # 識別結局章節
        ending_chapters = []
        for chapter in self.chapters:
            if not chapter.get('options') or len(chapter['options']) == 0:
                ending_chapters.append(chapter.get('id'))
        
        if not ending_chapters:
            self.warnings.append("沒有找到結局章節（沒有選項的章節）")
        else:
            self.log(f"找到 {len(ending_chapters)} 個結局章節: {ending_chapters}")
        
        # 檢查循環引用（簡單檢查）
        for chapter in self.chapters:
            chapter_id = chapter.get('id')
            if 'options' in chapter:
                for option in chapter['options']:
                    if option.get('next_id') == chapter_id:
                        self.warnings.append(f"章節 {chapter_id} 包含自我引用")
    
    def validate_conditional_content(self):
        """驗證條件內容"""
        print("⚙️ 檢查條件內容...")
        
        condition_pattern = r'\[\[IF\s+([^\]]+)\]\](.*?)\[\[ENDIF\]\]'
        game_state_vars = set()
        
        for chapter in self.chapters:
            chapter_id = chapter.get('id')
            chapter_ref = f"章節 {chapter_id}" if chapter_id else "未知章節"
            content = chapter.get('content', '')
            
            # 檢查條件內容語法
            matches = re.findall(condition_pattern, content, re.DOTALL)
            
            for condition, conditional_content in matches:
                condition = condition.strip()
                
                # 檢查布林條件
                if condition.startswith('NOT '):
                    var_name = condition[4:].strip()
                    if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', var_name):
                        game_state_vars.add(var_name)
                    else:
                        self.errors.append(f"{chapter_ref}: 無效的變數名稱 '{var_name}'")
                
                # 檢查數值比較條件
                elif any(op in condition for op in ['>=', '<=', '>', '<', '==', '!=']):
                    for op in ['>=', '<=', '>', '<', '==', '!=']:
                        if op in condition:
                            parts = condition.split(op, 1)
                            if len(parts) == 2:
                                var_name = parts[0].strip()
                                value = parts[1].strip()
                                
                                if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', var_name):
                                    game_state_vars.add(var_name)
                                else:
                                    self.errors.append(f"{chapter_ref}: 無效的變數名稱 '{var_name}'")
                                
                                # 檢查數值格式
                                try:
                                    float(value)
                                except ValueError:
                                    if not value.startswith('"') or not value.endswith('"'):
                                        self.warnings.append(f"{chapter_ref}: 條件值 '{value}' 可能需要引號")
                            break
                
                # 簡單布林條件
                elif re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', condition):
                    game_state_vars.add(condition)
                else:
                    self.errors.append(f"{chapter_ref}: 無效的條件語法 '{condition}'")
            
            # 檢查未閉合的條件標記
            if '[[IF' in content and content.count('[[IF') != content.count('[[ENDIF]]'):
                self.errors.append(f"{chapter_ref}: 條件標記未正確閉合")
        
        # 收集選項中的遊戲狀態變數
        for chapter in self.chapters:
            if 'options' in chapter:
                for option in chapter['options']:
                    if 'game_state' in option and isinstance(option['game_state'], dict):
                        game_state_vars.update(option['game_state'].keys())
        
        self.log(f"找到 {len(game_state_vars)} 個遊戲狀態變數: {sorted(game_state_vars)}")
        
        return game_state_vars
    
    def validate_content_quality(self):
        """驗證內容品質"""
        print("📝 檢查內容品質...")
        
        total_options = 0
        
        for chapter in self.chapters:
            chapter_id = chapter.get('id')
            chapter_ref = f"章節 {chapter_id}" if chapter_id else "未知章節"
            
            # 檢查標題品質
            title = chapter.get('title', '')
            if title:
                if title.isupper():
                    self.warnings.append(f"{chapter_ref}: 標題全部大寫，建議使用適當的大小寫")
                if title.endswith('...') or title.endswith('。'):
                    self.warnings.append(f"{chapter_ref}: 標題不應以省略號或句號結尾")
            
            # 檢查內容品質
            content = chapter.get('content', '')
            if content:
                if len(content.split()) < 5:
                    self.warnings.append(f"{chapter_ref}: 內容過短，可能影響故事體驗")
                
                # 檢查重複的標點符號
                if '!!' in content or '??' in content or '..' in content:
                    self.warnings.append(f"{chapter_ref}: 包含重複的標點符號")
            
            # 檢查選項品質
            options = chapter.get('options', [])
            total_options += len(options)
            
            if len(options) == 1:
                self.warnings.append(f"{chapter_ref}: 只有一個選項，可能不需要選擇")
            
            for option in options:
                option_text = option.get('text', '')
                if option_text:
                    if len(option_text) > 100:
                        self.warnings.append(f"{chapter_ref}: 選項文字過長")
                    if option_text.startswith('選擇') and len([o for o in options if o.get('text', '').startswith('選擇')]) > 1:
                        self.warnings.append(f"{chapter_ref}: 多個選項都以'選擇'開頭，建議多樣化")
        
        self.log(f"總選項數: {total_options}")
    
    def generate_statistics(self) -> Dict[str, Any]:
        """生成統計資訊"""
        stats = {
            "story_info": self.story_info,
            "total_chapters": len(self.chapters),
            "total_options": sum(len(chapter.get('options', [])) for chapter in self.chapters),
            "ending_chapters": len([c for c in self.chapters if not c.get('options')]),
            "conditional_chapters": len([c for c in self.chapters if '[[IF' in c.get('content', '')]),
            "avg_options_per_chapter": 0,
            "longest_chapter": 0,
            "shortest_chapter": float('inf')
        }
        
        if stats["total_chapters"] > 0:
            stats["avg_options_per_chapter"] = stats["total_options"] / stats["total_chapters"]
        
        for chapter in self.chapters:
            content_length = len(chapter.get('content', ''))
            stats["longest_chapter"] = max(stats["longest_chapter"], content_length)
            stats["shortest_chapter"] = min(stats["shortest_chapter"], content_length)
        
        if stats["shortest_chapter"] == float('inf'):
            stats["shortest_chapter"] = 0
        
        return stats
    
    def validate_all(self) -> bool:
        """執行所有驗證"""
        print("🚀 開始故事檔案驗證")
        print("=" * 70)
        
        # 執行各項驗證
        self.validate_story_info()
        self.validate_structure()
        self.validate_references()
        self.validate_logic_structure()
        game_state_vars = self.validate_conditional_content()
        self.validate_content_quality()
        
        # 生成統計資訊
        stats = self.generate_statistics()
        
        # 顯示結果
        print("\n" + "=" * 70)
        print("📊 驗證報告")
        print("=" * 70)
        
        print(f"📖 故事: {stats['story_info'].get('title', '未命名')}")
        print(f"🆔 ID: {stats['story_info'].get('story_id', '未知')}")
        print(f"👤 作者: {stats['story_info'].get('author', '未知')}")
        print(f"📝 版本: {stats['story_info'].get('version', '未知')}")
        print(f"📚 總章節數: {stats['total_chapters']}")
        print(f"🏁 結局章節數: {stats['ending_chapters']}")
        print(f"🔀 總選項數: {stats['total_options']}")
        print(f"📊 平均選項數: {stats['avg_options_per_chapter']:.1f}")
        print(f"⚙️ 包含條件內容的章節: {stats['conditional_chapters']}")
        print(f"📏 最長章節: {stats['longest_chapter']} 字元")
        print(f"📏 最短章節: {stats['shortest_chapter']} 字元")
        
        if game_state_vars:
            print(f"🎮 遊戲狀態變數: {len(game_state_vars)} 個")
            if self.verbose:
                print(f"   變數列表: {', '.join(sorted(game_state_vars))}")
        
        print("\n" + "=" * 70)
        
        # 顯示錯誤和警告
        if self.errors:
            print(f"❌ 發現 {len(self.errors)} 個錯誤:")
            for error in self.errors:
                print(f"   • {error}")
        else:
            print("✅ 沒有發現錯誤")
        
        if self.warnings:
            print(f"\n⚠️ 發現 {len(self.warnings)} 個警告:")
            for warning in self.warnings:
                print(f"   • {warning}")
        else:
            print("✅ 沒有發現警告")
        
        print("\n" + "=" * 70)
        
        if not self.errors and not self.warnings:
            print("🎉 故事檔案完美無缺！")
            return True
        elif not self.errors:
            print("✅ 故事檔案基本正確，但有一些建議改進的地方")
            return True
        else:
            print("❌ 故事檔案存在問題，需要修正")
            return False

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="故事檔案驗證工具")
    parser.add_argument("file", help="要驗證的故事檔案路徑")
    parser.add_argument("-v", "--verbose", action="store_true", help="顯示詳細資訊")
    
    args = parser.parse_args()
    
    print("🔧 Story Validator v1.1")
    print("支援新的多資料表架構和故事檔案格式")
    print("=" * 50)
    
    validator = StoryValidator(verbose=args.verbose)
    
    # 載入故事檔案
    if not validator.load_story(args.file):
        print("\n❌ 載入失敗:")
        for error in validator.errors:
            print(f"   • {error}")
        sys.exit(1)
    
    # 執行驗證
    success = validator.validate_all()
    
    if success:
        print("\n🎯 建議下一步:")
        print("1. 使用 story_converter.py 生成其他格式")
        print("2. 使用 seed_data.py 匯入到資料庫")
        print("3. 測試故事在遊戲引擎中的表現")
        sys.exit(0)
    else:
        print("\n🔧 修正建議:")
        print("1. 根據錯誤訊息修正故事檔案")
        print("2. 重新執行驗證")
        print("3. 參考文件了解正確的格式")
        sys.exit(1)

if __name__ == "__main__":
    main()

