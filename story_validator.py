"""
故事檔案驗證工具
檢查故事檔案的完整性、邏輯和格式
"""

import json
import argparse
import re
from typing import List, Dict, Set

class StoryValidator:
    """故事驗證器"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.chapters = []
        self.chapter_ids = set()
        
    def load_story(self, file_path: str) -> bool:
        """載入故事檔案"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.chapters = json.load(f)
            
            if not isinstance(self.chapters, list):
                self.errors.append("故事檔案必須是章節陣列")
                return False
            
            # 收集所有章節 ID
            self.chapter_ids = {chapter.get('id') for chapter in self.chapters if 'id' in chapter}
            
            print(f"✅ 成功載入 {len(self.chapters)} 個章節")
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
    
    def validate_structure(self):
        """驗證基本結構"""
        print("🔍 檢查基本結構...")
        
        required_fields = ['id', 'title', 'content', 'options']
        
        for i, chapter in enumerate(self.chapters):
            chapter_ref = f"章節 {i+1}"
            
            # 檢查必要欄位
            for field in required_fields:
                if field not in chapter:
                    self.errors.append(f"{chapter_ref}: 缺少必要欄位 '{field}'")
                elif not chapter[field] and field != 'options':  # options 可以是空陣列
                    self.warnings.append(f"{chapter_ref}: 欄位 '{field}' 是空的")
            
            # 檢查 ID 類型
            if 'id' in chapter:
                if not isinstance(chapter['id'], int):
                    self.errors.append(f"{chapter_ref}: ID 必須是整數")
                elif chapter['id'] <= 0:
                    self.errors.append(f"{chapter_ref}: ID 必須是正整數")
                else:
                    chapter_ref = f"章節 {chapter['id']}"
            
            # 檢查標題和內容
            if 'title' in chapter and not isinstance(chapter['title'], str):
                self.errors.append(f"{chapter_ref}: 標題必須是字串")
            
            if 'content' in chapter and not isinstance(chapter['content'], str):
                self.errors.append(f"{chapter_ref}: 內容必須是字串")
            
            # 檢查選項格式
            if 'options' in chapter:
                if not isinstance(chapter['options'], list):
                    self.errors.append(f"{chapter_ref}: 選項必須是陣列")
                else:
                    for j, option in enumerate(chapter['options']):
                        if not isinstance(option, dict):
                            self.errors.append(f"{chapter_ref}, 選項 {j+1}: 選項必須是物件")
                            continue
                        
                        if 'text' not in option:
                            self.errors.append(f"{chapter_ref}, 選項 {j+1}: 缺少 'text' 欄位")
                        elif not isinstance(option['text'], str):
                            self.errors.append(f"{chapter_ref}, 選項 {j+1}: 'text' 必須是字串")
                        
                        if 'next_id' not in option:
                            self.errors.append(f"{chapter_ref}, 選項 {j+1}: 缺少 'next_id' 欄位")
                        elif not isinstance(option['next_id'], int):
                            self.errors.append(f"{chapter_ref}, 選項 {j+1}: 'next_id' 必須是整數")
    
    def validate_references(self):
        """驗證章節引用"""
        print("🔗 檢查章節引用...")
        
        # 檢查重複 ID
        id_counts = {}
        for chapter in self.chapters:
            if 'id' in chapter:
                chapter_id = chapter['id']
                id_counts[chapter_id] = id_counts.get(chapter_id, 0) + 1
        
        for chapter_id, count in id_counts.items():
            if count > 1:
                self.errors.append(f"章節 ID {chapter_id} 重複出現 {count} 次")
        
        # 檢查選項引用
        for chapter in self.chapters:
            if 'id' not in chapter or 'options' not in chapter:
                continue
            
            chapter_id = chapter['id']
            for i, option in enumerate(chapter['options']):
                if 'next_id' in option:
                    next_id = option['next_id']
                    if next_id not in self.chapter_ids:
                        self.errors.append(f"章節 {chapter_id}, 選項 {i+1}: 引用不存在的章節 {next_id}")
    
    def validate_logic(self):
        """驗證邏輯結構"""
        print("🧠 檢查邏輯結構...")
        
        # 找出起始章節（通常是 ID 1）
        start_chapters = [ch for ch in self.chapters if ch.get('id') == 1]
        if not start_chapters:
            self.warnings.append("沒有找到 ID 為 1 的起始章節")
        
        # 找出結局章節（沒有選項的章節）
        ending_chapters = []
        for chapter in self.chapters:
            if 'options' in chapter and len(chapter['options']) == 0:
                ending_chapters.append(chapter.get('id'))
        
        if not ending_chapters:
            self.warnings.append("沒有找到結局章節（沒有選項的章節）")
        else:
            print(f"📖 找到 {len(ending_chapters)} 個結局章節: {ending_chapters}")
        
        # 檢查孤立章節（沒有被任何選項引用的章節，除了起始章節）
        referenced_ids = set()
        for chapter in self.chapters:
            if 'options' in chapter:
                for option in chapter['options']:
                    if 'next_id' in option:
                        referenced_ids.add(option['next_id'])
        
        orphaned_chapters = []
        for chapter in self.chapters:
            chapter_id = chapter.get('id')
            if chapter_id and chapter_id not in referenced_ids and chapter_id != 1:
                orphaned_chapters.append(chapter_id)
        
        if orphaned_chapters:
            self.warnings.append(f"發現孤立章節（沒有被引用）: {orphaned_chapters}")
    
    def validate_conditions(self):
        """驗證條件語法"""
        print("⚙️ 檢查條件語法...")
        
        condition_pattern = r'\[\[IF\s+([^]]+)\]\](.*?)\[\[ENDIF\]\]'
        
        for chapter in self.chapters:
            if 'content' not in chapter:
                continue
            
            chapter_id = chapter.get('id', '未知')
            content = chapter['content']
            
            # 檢查條件語法
            conditions = re.findall(condition_pattern, content, re.DOTALL)
            
            for condition, conditional_content in conditions:
                condition = condition.strip()
                
                # 檢查條件格式
                if not condition:
                    self.errors.append(f"章節 {chapter_id}: 空的條件語句")
                    continue
                
                # 檢查常見的條件變數命名
                if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', condition):
                    self.warnings.append(f"章節 {chapter_id}: 條件變數 '{condition}' 可能不符合命名規範")
                
                # 檢查條件內容
                if not conditional_content.strip():
                    self.warnings.append(f"章節 {chapter_id}: 條件 '{condition}' 的內容是空的")
            
            # 檢查未閉合的條件
            if_count = content.count('[[IF')
            endif_count = content.count('[[ENDIF]]')
            
            if if_count != endif_count:
                self.errors.append(f"章節 {chapter_id}: IF 和 ENDIF 數量不匹配 ({if_count} vs {endif_count})")
    
    def validate_content_quality(self):
        """驗證內容品質"""
        print("📝 檢查內容品質...")
        
        for chapter in self.chapters:
            chapter_id = chapter.get('id', '未知')
            
            # 檢查標題長度
            if 'title' in chapter:
                title = chapter['title']
                if len(title) > 50:
                    self.warnings.append(f"章節 {chapter_id}: 標題過長 ({len(title)} 字元)")
                elif len(title) < 2:
                    self.warnings.append(f"章節 {chapter_id}: 標題過短")
            
            # 檢查內容長度
            if 'content' in chapter:
                content = chapter['content']
                if len(content) > 2000:
                    self.warnings.append(f"章節 {chapter_id}: 內容過長 ({len(content)} 字元)")
                elif len(content) < 10:
                    self.warnings.append(f"章節 {chapter_id}: 內容過短")
            
            # 檢查選項數量
            if 'options' in chapter:
                options = chapter['options']
                if len(options) > 5:
                    self.warnings.append(f"章節 {chapter_id}: 選項過多 ({len(options)} 個)")
                elif len(options) == 1:
                    self.warnings.append(f"章節 {chapter_id}: 只有一個選項，考慮是否需要選擇")
    
    def generate_report(self):
        """生成驗證報告"""
        print("\n" + "=" * 60)
        print("📊 驗證報告")
        print("=" * 60)
        
        # 基本統計
        print(f"📚 總章節數: {len(self.chapters)}")
        
        ending_count = sum(1 for ch in self.chapters if ch.get('options', []) == [])
        print(f"🏁 結局章節數: {ending_count}")
        
        total_options = sum(len(ch.get('options', [])) for ch in self.chapters)
        print(f"🔀 總選項數: {total_options}")
        
        # 錯誤報告
        if self.errors:
            print(f"\n❌ 發現 {len(self.errors)} 個錯誤:")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")
        else:
            print("\n✅ 沒有發現錯誤")
        
        # 警告報告
        if self.warnings:
            print(f"\n⚠️  發現 {len(self.warnings)} 個警告:")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")
        else:
            print("\n✅ 沒有發現警告")
        
        # 總結
        print("\n" + "=" * 60)
        if not self.errors and not self.warnings:
            print("🎉 故事檔案完美無缺！")
        elif not self.errors:
            print("✅ 故事檔案基本正確，但有一些建議改進的地方")
        else:
            print("❌ 故事檔案存在問題，需要修正")
        
        return len(self.errors) == 0
    
    def validate_all(self, file_path: str) -> bool:
        """執行完整驗證"""
        if not self.load_story(file_path):
            return False
        
        self.validate_structure()
        self.validate_references()
        self.validate_logic()
        self.validate_conditions()
        self.validate_content_quality()
        
        return self.generate_report()

def main():
    """主程式"""
    parser = argparse.ArgumentParser(
        description="故事檔案驗證工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用範例:
  python story_validator.py story.json              # 驗證故事檔案
  python story_validator.py example_simple_story.json  # 驗證範例故事
        """
    )
    
    parser.add_argument('file', help='要驗證的故事 JSON 檔案')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🔍 故事檔案驗證工具")
    print("=" * 60)
    
    validator = StoryValidator()
    success = validator.validate_all(args.file)
    
    # 返回適當的退出碼
    exit(0 if success else 1)

if __name__ == "__main__":
    main()

