"""
故事格式轉換工具
支援在不同格式之間轉換故事資料
"""

import json
import argparse
import csv
from typing import List, Dict

class StoryConverter:
    """故事格式轉換器"""
    
    def __init__(self):
        self.chapters = []
    
    def load_json(self, file_path: str) -> bool:
        """從 JSON 檔案載入故事"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.chapters = json.load(f)
            print(f"✅ 從 JSON 載入 {len(self.chapters)} 個章節")
            return True
        except Exception as e:
            print(f"❌ 載入 JSON 失敗: {e}")
            return False
    
    def save_json(self, file_path: str) -> bool:
        """儲存為 JSON 檔案"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.chapters, f, ensure_ascii=False, indent=2)
            print(f"✅ 儲存為 JSON: {file_path}")
            return True
        except Exception as e:
            print(f"❌ 儲存 JSON 失敗: {e}")
            return False
    
    def save_csv(self, file_path: str) -> bool:
        """儲存為 CSV 檔案"""
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # 寫入標頭
                writer.writerow(['ID', '標題', '內容', '選項數量', '選項詳情'])
                
                # 寫入章節資料
                for chapter in self.chapters:
                    options_detail = []
                    for i, option in enumerate(chapter.get('options', []), 1):
                        options_detail.append(f"{i}. {option.get('text', '')} -> {option.get('next_id', '')}")
                    
                    writer.writerow([
                        chapter.get('id', ''),
                        chapter.get('title', ''),
                        chapter.get('content', '').replace('\n', '\\n'),
                        len(chapter.get('options', [])),
                        ' | '.join(options_detail)
                    ])
            
            print(f"✅ 儲存為 CSV: {file_path}")
            return True
        except Exception as e:
            print(f"❌ 儲存 CSV 失敗: {e}")
            return False
    
    def save_markdown(self, file_path: str) -> bool:
        """儲存為 Markdown 檔案"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("# 故事內容\n\n")
                
                for chapter in self.chapters:
                    chapter_id = chapter.get('id', '未知')
                    title = chapter.get('title', '無標題')
                    content = chapter.get('content', '')
                    options = chapter.get('options', [])
                    
                    # 寫入章節標題
                    f.write(f"## 第 {chapter_id} 章：{title}\n\n")
                    
                    # 寫入內容
                    f.write(f"{content}\n\n")
                    
                    # 寫入選項
                    if options:
                        f.write("### 選項\n\n")
                        for i, option in enumerate(options, 1):
                            text = option.get('text', '')
                            next_id = option.get('next_id', '')
                            f.write(f"{i}. {text} → 第 {next_id} 章\n")
                        f.write("\n")
                    else:
                        f.write("**（故事結局）**\n\n")
                    
                    f.write("---\n\n")
            
            print(f"✅ 儲存為 Markdown: {file_path}")
            return True
        except Exception as e:
            print(f"❌ 儲存 Markdown 失敗: {e}")
            return False
    
    def save_flowchart(self, file_path: str) -> bool:
        """儲存為流程圖格式（Mermaid）"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("```mermaid\n")
                f.write("flowchart TD\n")
                
                # 定義節點
                for chapter in self.chapters:
                    chapter_id = chapter.get('id', '')
                    title = chapter.get('title', '').replace('"', '\\"')
                    options = chapter.get('options', [])
                    
                    if options:
                        # 有選項的章節
                        f.write(f'    {chapter_id}["{title}"]\n')
                    else:
                        # 結局章節
                        f.write(f'    {chapter_id}["{title}"]:::ending\n')
                
                f.write("\n")
                
                # 定義連接
                for chapter in self.chapters:
                    chapter_id = chapter.get('id', '')
                    options = chapter.get('options', [])
                    
                    for option in options:
                        next_id = option.get('next_id', '')
                        text = option.get('text', '').replace('"', '\\"')
                        if len(text) > 20:
                            text = text[:17] + "..."
                        f.write(f'    {chapter_id} -->|"{text}"| {next_id}\n')
                
                # 定義樣式
                f.write("\n")
                f.write("    classDef ending fill:#ffcccc,stroke:#ff6666,stroke-width:2px\n")
                f.write("```\n")
            
            print(f"✅ 儲存為流程圖: {file_path}")
            return True
        except Exception as e:
            print(f"❌ 儲存流程圖失敗: {e}")
            return False
    
    def generate_statistics(self) -> Dict:
        """生成故事統計資訊"""
        stats = {
            'total_chapters': len(self.chapters),
            'ending_chapters': 0,
            'total_options': 0,
            'max_options': 0,
            'min_options': float('inf'),
            'avg_content_length': 0,
            'longest_chapter': '',
            'shortest_chapter': '',
            'chapter_connections': {}
        }
        
        total_content_length = 0
        longest_content = 0
        shortest_content = float('inf')
        
        for chapter in self.chapters:
            chapter_id = chapter.get('id', '')
            title = chapter.get('title', '')
            content = chapter.get('content', '')
            options = chapter.get('options', [])
            
            # 統計選項
            option_count = len(options)
            stats['total_options'] += option_count
            
            if option_count == 0:
                stats['ending_chapters'] += 1
            
            stats['max_options'] = max(stats['max_options'], option_count)
            if option_count > 0:
                stats['min_options'] = min(stats['min_options'], option_count)
            
            # 統計內容長度
            content_length = len(content)
            total_content_length += content_length
            
            if content_length > longest_content:
                longest_content = content_length
                stats['longest_chapter'] = f"第 {chapter_id} 章：{title}"
            
            if content_length < shortest_content:
                shortest_content = content_length
                stats['shortest_chapter'] = f"第 {chapter_id} 章：{title}"
            
            # 統計連接
            stats['chapter_connections'][chapter_id] = [opt.get('next_id') for opt in options]
        
        if stats['min_options'] == float('inf'):
            stats['min_options'] = 0
        
        if stats['total_chapters'] > 0:
            stats['avg_content_length'] = total_content_length / stats['total_chapters']
        
        return stats
    
    def print_statistics(self):
        """印出故事統計資訊"""
        stats = self.generate_statistics()
        
        print("\n📊 故事統計資訊")
        print("=" * 40)
        print(f"總章節數: {stats['total_chapters']}")
        print(f"結局章節數: {stats['ending_chapters']}")
        print(f"總選項數: {stats['total_options']}")
        print(f"最多選項數: {stats['max_options']}")
        print(f"最少選項數: {stats['min_options']}")
        print(f"平均內容長度: {stats['avg_content_length']:.1f} 字元")
        print(f"最長章節: {stats['longest_chapter']}")
        print(f"最短章節: {stats['shortest_chapter']}")

def main():
    """主程式"""
    parser = argparse.ArgumentParser(
        description="故事格式轉換工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用範例:
  python story_converter.py story.json --csv story.csv           # 轉換為 CSV
  python story_converter.py story.json --markdown story.md       # 轉換為 Markdown
  python story_converter.py story.json --flowchart story.mmd     # 轉換為流程圖
  python story_converter.py story.json --stats                   # 顯示統計資訊
        """
    )
    
    parser.add_argument('input', help='輸入的 JSON 故事檔案')
    parser.add_argument('--csv', help='輸出 CSV 檔案路徑')
    parser.add_argument('--markdown', help='輸出 Markdown 檔案路徑')
    parser.add_argument('--flowchart', help='輸出流程圖檔案路徑（Mermaid 格式）')
    parser.add_argument('--stats', action='store_true', help='顯示統計資訊')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🔄 故事格式轉換工具")
    print("=" * 60)
    
    converter = StoryConverter()
    
    # 載入故事
    if not converter.load_json(args.input):
        exit(1)
    
    # 執行轉換
    success = True
    
    if args.csv:
        success &= converter.save_csv(args.csv)
    
    if args.markdown:
        success &= converter.save_markdown(args.markdown)
    
    if args.flowchart:
        success &= converter.save_flowchart(args.flowchart)
    
    if args.stats:
        converter.print_statistics()
    
    if not any([args.csv, args.markdown, args.flowchart, args.stats]):
        print("⚠️  請指定至少一個輸出格式或 --stats 參數")
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("✨ 轉換完成")
    else:
        print("❌ 轉換過程中發生錯誤")
    
    exit(0 if success else 1)

if __name__ == "__main__":
    main()

