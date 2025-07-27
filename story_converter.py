#!/usr/bin/env python3
"""
故事格式轉換工具
支援在不同格式之間轉換故事資料
支援新的多資料表架構和故事檔案格式
"""

import json
import argparse
import csv
import sys
import re
from typing import List, Dict, Any, Optional
from datetime import datetime

class StoryConverter:
    """故事格式轉換器"""
    
    def __init__(self, verbose: bool = False):
        self.story_data = None
        self.story_info = {}
        self.chapters = []
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
                    "version": "1.0",
                    "created_at": datetime.now().isoformat()
                }
                
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
                            "version": "1.0",
                            "created_at": datetime.now().isoformat()
                        }
                    else:
                        print("❌ 無法識別的故事檔案格式")
                        return False
            else:
                print("❌ 故事檔案格式錯誤")
                return False
            
            print(f"✅ 成功載入故事: {self.story_info.get('title', '未命名')}")
            print(f"📚 章節數量: {len(self.chapters)}")
            return True
            
        except FileNotFoundError:
            print(f"❌ 找不到檔案: {file_path}")
            return False
        except json.JSONDecodeError as e:
            print(f"❌ JSON 格式錯誤: {e}")
            return False
        except Exception as e:
            print(f"❌ 載入檔案時發生錯誤: {e}")
            return False
    
    def save_json(self, file_path: str, format_type: str = "new") -> bool:
        """儲存為 JSON 檔案"""
        try:
            if format_type == "new":
                # 新格式
                output_data = {
                    "story_info": self.story_info,
                    "chapters": self.chapters
                }
            else:
                # 舊格式（僅章節陣列）
                output_data = self.chapters
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 儲存為 JSON ({format_type} 格式): {file_path}")
            return True
        except Exception as e:
            print(f"❌ 儲存 JSON 失敗: {e}")
            return False
    
    def save_csv(self, file_path: str) -> bool:
        """儲存為 CSV 檔案"""
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # 寫入故事資訊
                writer.writerow(['故事資訊'])
                writer.writerow(['故事ID', self.story_info.get('story_id', '')])
                writer.writerow(['標題', self.story_info.get('title', '')])
                writer.writerow(['描述', self.story_info.get('description', '')])
                writer.writerow(['作者', self.story_info.get('author', '')])
                writer.writerow(['版本', self.story_info.get('version', '')])
                writer.writerow([])  # 空行
                
                # 寫入章節標頭
                writer.writerow(['章節ID', '標題', '內容', '選項數量', '選項詳情', '遊戲狀態變更'])
                
                # 寫入章節資料
                for chapter in self.chapters:
                    options_detail = []
                    game_state_changes = []
                    
                    for i, option in enumerate(chapter.get('options', []), 1):
                        option_text = option.get('text', '')
                        next_id = option.get('next_id', '')
                        options_detail.append(f"{i}. {option_text} -> 章節{next_id}")
                        
                        # 收集遊戲狀態變更
                        if 'game_state' in option:
                            for key, value in option['game_state'].items():
                                game_state_changes.append(f"{key}={value}")
                    
                    writer.writerow([
                        chapter.get('id', ''),
                        chapter.get('title', ''),
                        chapter.get('content', '').replace('\n', '\\n'),
                        len(chapter.get('options', [])),
                        ' | '.join(options_detail),
                        ' | '.join(game_state_changes)
                    ])
            
            print(f"✅ 儲存為 CSV: {file_path}")
            return True
        except Exception as e:
            print(f"❌ 儲存 CSV 失敗: {e}")
            return False
    
    def process_conditional_content(self, content: str, show_conditions: bool = True) -> str:
        """處理條件內容"""
        if not show_conditions:
            # 移除所有條件標記，只保留內容
            content = re.sub(r'\[\[IF\s+[^\]]+\]\](.*?)\[\[ENDIF\]\]', r'\1', content, flags=re.DOTALL)
        else:
            # 保留條件標記但格式化
            def replace_condition(match):
                condition = match.group(1).strip()
                conditional_content = match.group(2)
                return f"[條件: {condition}] {conditional_content} [/條件]"
            
            content = re.sub(r'\[\[IF\s+([^\]]+)\]\](.*?)\[\[ENDIF\]\]', replace_condition, content, flags=re.DOTALL)
        
        return content
    
    def save_markdown(self, file_path: str, include_conditions: bool = True) -> bool:
        """儲存為 Markdown 檔案"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                # 寫入故事資訊
                f.write(f"# {self.story_info.get('title', '未命名故事')}\n\n")
                
                if self.story_info.get('description'):
                    f.write(f"**描述：** {self.story_info['description']}\n\n")
                
                f.write("## 故事資訊\n\n")
                f.write(f"- **故事ID：** {self.story_info.get('story_id', '未知')}\n")
                f.write(f"- **作者：** {self.story_info.get('author', '未知')}\n")
                f.write(f"- **版本：** {self.story_info.get('version', '未知')}\n")
                f.write(f"- **章節數：** {len(self.chapters)}\n")
                f.write(f"- **總選項數：** {sum(len(c.get('options', [])) for c in self.chapters)}\n\n")
                
                # 生成目錄
                f.write("## 目錄\n\n")
                for chapter in self.chapters:
                    chapter_id = chapter.get('id', '未知')
                    title = chapter.get('title', '無標題')
                    f.write(f"- [第 {chapter_id} 章：{title}](#第-{chapter_id}-章{title.replace(' ', '-').lower()})\n")
                f.write("\n")
                
                # 寫入章節內容
                f.write("## 章節內容\n\n")
                
                for chapter in self.chapters:
                    chapter_id = chapter.get('id', '未知')
                    title = chapter.get('title', '無標題')
                    content = chapter.get('content', '')
                    options = chapter.get('options', [])
                    
                    # 處理條件內容
                    processed_content = self.process_conditional_content(content, include_conditions)
                    
                    # 寫入章節標題
                    f.write(f"### 第 {chapter_id} 章：{title}\n\n")
                    
                    # 寫入內容
                    f.write(f"{processed_content}\n\n")
                    
                    # 寫入選項
                    if options:
                        f.write("#### 選項\n\n")
                        for i, option in enumerate(options, 1):
                            text = option.get('text', '')
                            next_id = option.get('next_id', '')
                            
                            f.write(f"{i}. **{text}** → [第 {next_id} 章](#第-{next_id}-章)\n")
                            
                            # 顯示遊戲狀態變更
                            if 'game_state' in option and option['game_state']:
                                f.write(f"   - *狀態變更：*")
                                for key, value in option['game_state'].items():
                                    f.write(f" {key}={value}")
                                f.write("\n")
                            
                            # 顯示條件
                            if 'condition' in option and option['condition']:
                                f.write(f"   - *條件：* {option['condition']}\n")
                        
                        f.write("\n")
                    else:
                        f.write("**（故事結局）**\n\n")
                    
                    f.write("---\n\n")
                
                # 添加統計資訊
                self._add_statistics_to_markdown(f)
            
            print(f"✅ 儲存為 Markdown: {file_path}")
            return True
        except Exception as e:
            print(f"❌ 儲存 Markdown 失敗: {e}")
            return False
    
    def save_flowchart(self, file_path: str) -> bool:
        """儲存為 Mermaid 流程圖"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("```mermaid\n")
                f.write("flowchart TD\n")
                f.write(f"    %% {self.story_info.get('title', '未命名故事')} 流程圖\n\n")
                
                # 定義節點
                for chapter in self.chapters:
                    chapter_id = chapter.get('id', 0)
                    title = chapter.get('title', '無標題')
                    options = chapter.get('options', [])
                    
                    # 根據章節類型設定樣式
                    if chapter_id == 1:
                        # 起始章節
                        f.write(f"    C{chapter_id}[\"🚀 {title}\"]:::start\n")
                    elif not options:
                        # 結局章節
                        f.write(f"    C{chapter_id}[\"🏁 {title}\"]:::ending\n")
                    else:
                        # 普通章節
                        f.write(f"    C{chapter_id}[\"{title}\"]:::normal\n")
                
                f.write("\n")
                
                # 定義連接
                for chapter in self.chapters:
                    chapter_id = chapter.get('id', 0)
                    options = chapter.get('options', [])
                    
                    for i, option in enumerate(options):
                        next_id = option.get('next_id', 0)
                        text = option.get('text', '')
                        
                        # 縮短選項文字以適合流程圖
                        if len(text) > 20:
                            text = text[:17] + "..."
                        
                        # 檢查是否有條件
                        if 'condition' in option and option['condition']:
                            f.write(f"    C{chapter_id} -->|\"⚙️ {text}\"| C{next_id}\n")
                        else:
                            f.write(f"    C{chapter_id} -->|\"{text}\"| C{next_id}\n")
                
                f.write("\n")
                
                # 定義樣式
                f.write("    classDef start fill:#e1f5fe,stroke:#01579b,stroke-width:3px\n")
                f.write("    classDef ending fill:#f3e5f5,stroke:#4a148c,stroke-width:3px\n")
                f.write("    classDef normal fill:#f1f8e9,stroke:#33691e,stroke-width:2px\n")
                
                f.write("```\n")
            
            print(f"✅ 儲存為 Mermaid 流程圖: {file_path}")
            return True
        except Exception as e:
            print(f"❌ 儲存流程圖失敗: {e}")
            return False
    
    def save_database_sql(self, file_path: str) -> bool:
        """儲存為資料庫 SQL 腳本"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                story_id = self.story_info.get('story_id', 'unknown')
                table_name = f"story_{story_id}"
                
                f.write("-- Story Engine Database Script\n")
                f.write(f"-- Generated for story: {self.story_info.get('title', '未命名')}\n")
                f.write(f"-- Story ID: {story_id}\n")
                f.write(f"-- Generated at: {datetime.now().isoformat()}\n\n")
                
                # 故事註冊表插入語句
                f.write("-- Insert into story registry\n")
                f.write("INSERT INTO story_registry (story_id, table_name, title, description, author, version, created_at) VALUES (\n")
                f.write(f"    '{story_id}',\n")
                f.write(f"    '{table_name}',\n")
                
                title_escaped = self.story_info.get('title', '').replace("'", "''")
                description_escaped = self.story_info.get('description', '').replace("'", "''")
                author_escaped = self.story_info.get('author', '').replace("'", "''")
                
                f.write(f"    '{title_escaped}',\n")
                f.write(f"    '{description_escaped}',\n")
                f.write(f"    '{author_escaped}',\n")
                f.write(f"    '{self.story_info.get('version', '1.0')}',\n")
                f.write(f"    '{datetime.now().isoformat()}'\n")
                f.write(");\n\n")
                
                # 故事表創建語句
                f.write(f"-- Create story table: {table_name}\n")
                f.write(f"CREATE TABLE IF NOT EXISTS {table_name} (\n")
                f.write("    id INTEGER PRIMARY KEY,\n")
                f.write("    title TEXT NOT NULL,\n")
                f.write("    content TEXT NOT NULL,\n")
                f.write("    options TEXT,\n")
                f.write("    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\n")
                f.write("    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n")
                f.write(");\n\n")
                
                # 章節資料插入語句
                f.write(f"-- Insert chapters into {table_name}\n")
                for chapter in self.chapters:
                    chapter_id = chapter.get('id', 0)
                    title_escaped = chapter.get('title', '').replace("'", "''")
                    content_escaped = chapter.get('content', '').replace("'", "''")
                    options_escaped = json.dumps(chapter.get('options', []), ensure_ascii=False).replace("'", "''")
                    
                    f.write(f"INSERT INTO {table_name} (id, title, content, options) VALUES (\n")
                    f.write(f"    {chapter_id},\n")
                    f.write(f"    '{title_escaped}',\n")
                    f.write(f"    '{content_escaped}',\n")
                    f.write(f"    '{options_escaped}'\n")
                    f.write(");\n\n")
                
                # 添加索引
                f.write(f"-- Create indexes for {table_name}\n")
                f.write(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_id ON {table_name}(id);\n")
            
            print(f"✅ 儲存為 SQL 腳本: {file_path}")
            return True
        except Exception as e:
            print(f"❌ 儲存 SQL 腳本失敗: {e}")
            return False
    
    def _add_statistics_to_markdown(self, f):
        """添加統計資訊到 Markdown"""
        f.write("## 統計資訊\n\n")
        
        total_chapters = len(self.chapters)
        total_options = sum(len(c.get('options', [])) for c in self.chapters)
        ending_chapters = len([c for c in self.chapters if not c.get('options')])
        conditional_chapters = len([c for c in self.chapters if '[[IF' in c.get('content', '')])
        
        f.write(f"- **總章節數：** {total_chapters}\n")
        f.write(f"- **總選項數：** {total_options}\n")
        f.write(f"- **平均選項數：** {total_options/total_chapters:.1f}\n")
        f.write(f"- **結局章節數：** {ending_chapters}\n")
        f.write(f"- **包含條件內容的章節：** {conditional_chapters}\n")
        
        # 收集遊戲狀態變數
        game_state_vars = set()
        for chapter in self.chapters:
            content = chapter.get('content', '')
            # 從條件內容中提取變數
            conditions = re.findall(r'\[\[IF\s+([^\]]+)\]\]', content)
            for condition in conditions:
                condition = condition.strip()
                if condition.startswith('NOT '):
                    var_name = condition[4:].strip()
                    if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', var_name):
                        game_state_vars.add(var_name)
                elif any(op in condition for op in ['>=', '<=', '>', '<', '==', '!=']):
                    for op in ['>=', '<=', '>', '<', '==', '!=']:
                        if op in condition:
                            var_name = condition.split(op)[0].strip()
                            if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', var_name):
                                game_state_vars.add(var_name)
                            break
                elif re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', condition):
                    game_state_vars.add(condition)
            
            # 從選項中提取變數
            for option in chapter.get('options', []):
                if 'game_state' in option and isinstance(option['game_state'], dict):
                    game_state_vars.update(option['game_state'].keys())
        
        if game_state_vars:
            f.write(f"- **遊戲狀態變數：** {len(game_state_vars)} 個\n")
            f.write(f"  - {', '.join(sorted(game_state_vars))}\n")
        
        f.write("\n")
    
    def show_statistics(self):
        """顯示統計資訊"""
        print("\n📊 故事統計資訊")
        print("=" * 50)
        
        total_chapters = len(self.chapters)
        total_options = sum(len(c.get('options', [])) for c in self.chapters)
        ending_chapters = len([c for c in self.chapters if not c.get('options')])
        conditional_chapters = len([c for c in self.chapters if '[[IF' in c.get('content', '')])
        
        print(f"📖 故事標題: {self.story_info.get('title', '未命名')}")
        print(f"🆔 故事ID: {self.story_info.get('story_id', '未知')}")
        print(f"👤 作者: {self.story_info.get('author', '未知')}")
        print(f"📝 版本: {self.story_info.get('version', '未知')}")
        print(f"📚 總章節數: {total_chapters}")
        print(f"🔀 總選項數: {total_options}")
        print(f"📊 平均選項數: {total_options/total_chapters:.1f}")
        print(f"🏁 結局章節數: {ending_chapters}")
        print(f"⚙️ 包含條件內容的章節: {conditional_chapters}")
        
        # 最長和最短章節
        if self.chapters:
            chapter_lengths = [(c.get('id'), len(c.get('content', ''))) for c in self.chapters]
            longest = max(chapter_lengths, key=lambda x: x[1])
            shortest = min(chapter_lengths, key=lambda x: x[1])
            
            print(f"📏 最長章節: 第 {longest[0]} 章 ({longest[1]} 字元)")
            print(f"📏 最短章節: 第 {shortest[0]} 章 ({shortest[1]} 字元)")

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="故事格式轉換工具")
    parser.add_argument("input", help="輸入的故事檔案路徑")
    parser.add_argument("-v", "--verbose", action="store_true", help="顯示詳細資訊")
    parser.add_argument("--stats", action="store_true", help="顯示統計資訊")
    
    # 輸出格式選項
    parser.add_argument("--json", help="輸出為 JSON 檔案")
    parser.add_argument("--json-old", help="輸出為舊格式 JSON 檔案")
    parser.add_argument("--csv", help="輸出為 CSV 檔案")
    parser.add_argument("--markdown", help="輸出為 Markdown 檔案")
    parser.add_argument("--flowchart", help="輸出為 Mermaid 流程圖")
    parser.add_argument("--database", help="輸出為資料庫 SQL 腳本")
    
    args = parser.parse_args()
    
    print("🔧 Story Converter v1.1")
    print("支援新的多資料表架構和故事檔案格式")
    print("=" * 50)
    
    converter = StoryConverter(verbose=args.verbose)
    
    # 載入故事檔案
    if not converter.load_story(args.input):
        sys.exit(1)
    
    # 顯示統計資訊
    if args.stats:
        converter.show_statistics()
    
    # 執行轉換
    success_count = 0
    total_count = 0
    
    if args.json:
        total_count += 1
        if converter.save_json(args.json, "new"):
            success_count += 1
    
    if args.json_old:
        total_count += 1
        if converter.save_json(args.json_old, "old"):
            success_count += 1
    
    if args.csv:
        total_count += 1
        if converter.save_csv(args.csv):
            success_count += 1
    
    if args.markdown:
        total_count += 1
        if converter.save_markdown(args.markdown):
            success_count += 1
    
    if args.flowchart:
        total_count += 1
        if converter.save_flowchart(args.flowchart):
            success_count += 1
    
    if args.database:
        total_count += 1
        if converter.save_database_sql(args.database):
            success_count += 1
    
    if total_count == 0:
        print("\n⚠️ 沒有指定輸出格式")
        print("使用 --help 查看可用的輸出選項")
        sys.exit(1)
    
    print(f"\n📊 轉換完成: {success_count}/{total_count} 成功")
    
    if success_count == total_count:
        print("🎉 所有轉換都成功完成！")
        sys.exit(0)
    else:
        print("⚠️ 部分轉換失敗，請檢查錯誤訊息")
        sys.exit(1)

if __name__ == "__main__":
    main()

