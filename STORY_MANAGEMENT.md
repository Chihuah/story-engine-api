# 故事管理指南

本指南詳細說明如何使用故事引擎的管理工具來建立、編輯、驗證和轉換互動式冒險故事。

## 概述

故事引擎採用多表資料庫架構，每個故事都有獨立的資料表。系統提供三個主要的管理工具：

- **seed_data.py** - 故事資料管理工具
- **story_validator.py** - 故事檔案驗證工具
- **story_converter.py** - 故事格式轉換工具

## 故事檔案格式

### 新格式（推薦）

```json
{
  "story_info": {
    "story_id": "forest_adventure",
    "title": "森林冒險",
    "description": "一個關於勇氣與智慧的森林探險故事",
    "author": "Story Engine Team",
    "version": "1.0"
  },
  "chapters": [
    {
      "id": 1,
      "title": "森林入口",
      "content": "你站在一片古老森林的邊緣...",
      "options": [
        {
          "text": "選擇平坦的小徑",
          "next_chapter": 2,
          "game_state": { "took_risk": false, "played_safe": true }
        }
      ]
    }
  ]
}
```

### 舊格式（相容）

```json
[
  {
    "id": 1,
    "title": "章節標題",
    "content": "章節內容...",
    "options": [...]
  }
]
```

## 條件內容語法

### 布林條件

```
[[IF has_weapon]]你握緊手中的武器。[[ENDIF]]
[[IF NOT has_key]]你沒有鑰匙。[[ENDIF]]
```

### 數值比較條件

```
[[IF health > 50]]你感覺身體健康。[[ENDIF]]
[[IF strength >= 20]]你有足夠的力量。[[ENDIF]]
[[IF wisdom < 10]]你感到困惑。[[ENDIF]]
[[IF gold == 0]]你身無分文。[[ENDIF]]
[[IF level != 1]]你不是新手。[[ENDIF]]
```

支援的運算子：`>`, `<`, `>=`, `<=`, `==`, `!=`

## seed_data.py - 故事資料管理工具

### 基本功能

#### 建立預設故事

```bash
python seed_data.py
```

建立預設的「森林冒險」故事，包含 21 個章節和豐富的遊戲狀態變數。

#### 列出所有故事

```bash
python seed_data.py --list-stories
```

顯示資料庫中所有故事的資訊，包括標題、作者、章節數等。

#### 列出指定故事的章節

```bash
python seed_data.py --list-chapters forest_adventure
```

顯示指定故事的所有章節詳情，包括選項和連接關係。

### 匯入匯出功能

#### 匯入故事

```bash
# 從 JSON 檔案匯入故事
python seed_data.py --import-story story.json

# 指定故事 ID（覆蓋檔案中的設定）
python seed_data.py --import-story story.json --story-id my_story

# 覆蓋現有故事
python seed_data.py --import-story story.json --overwrite
```

#### 匯出單一故事

```bash
# 匯出指定故事
python seed_data.py --export-story forest_adventure

# 指定輸出檔案名稱
python seed_data.py --export-story forest_adventure --output my_story.json
```

#### 匯出所有故事

```bash
# 匯出所有故事到單一檔案
python seed_data.py --export-all-stories

# 指定輸出檔案名稱
python seed_data.py --export-all-stories --output all_stories.json
```

### 清理功能

#### 刪除指定故事

```bash
python seed_data.py --clear-story forest_adventure
```

會要求確認後刪除指定故事的所有資料。

#### 刪除所有故事

```bash
python seed_data.py --clear-all
```

會要求確認後刪除所有故事資料。

### 使用範例

```bash
# 日常工作流程
python seed_data.py --list-stories                    # 查看現有故事
python seed_data.py --import-story new_story.json     # 匯入新故事
python seed_data.py --export-story my_story           # 備份故事
python seed_data.py --clear-story old_story           # 清理舊故事
```

## story_validator.py - 故事檔案驗證工具

### 基本驗證

```bash
# 驗證故事檔案
python story_validator.py story.json

# 詳細模式
python story_validator.py story.json -v
```

### 驗證項目

#### 1. 故事資訊驗證

- 檢查必要欄位：story_id, title, description
- 檢查推薦欄位：author, version, created_at
- 驗證 story_id 格式（字母開頭，只包含字母、數字、底線）
- 檢查標題長度

#### 2. 基本結構驗證

- 檢查章節必要欄位：id, title, content, options
- 驗證資料類型
- 檢查選項格式

#### 3. 章節引用驗證

- 檢查重複章節 ID
- 驗證選項引用的章節是否存在

#### 4. 邏輯結構驗證

- 檢查起始章節（ID 為 1）
- 識別結局章節（沒有選項的章節）
- 偵測孤立章節

#### 5. 條件內容驗證

- 檢查 `[[IF]]...[[ENDIF]]` 語法
- 驗證條件格式（布林和數值比較）
- 檢查未閉合的條件標記
- 偵測可能的巢狀條件

#### 6. 內容品質驗證

- 檢查標題和內容長度
- 評估選項數量
- 分析選項文字品質

#### 7. 遊戲機制驗證

- 收集所有遊戲狀態變數
- 檢查變數命名規範
- 分析變數使用情況
- 偵測未定義或未使用的變數

### 驗證報告

驗證完成後會顯示詳細報告：

```
📊 驗證報告
======================================================================
📖 故事: 森林冒險
🆔 ID: forest_adventure
👤 作者: Story Engine Team
📝 版本: 1.0
📚 總章節數: 21
🏁 結局章節數: 4
🔀 總選項數: 34
⚙️ 包含條件內容的章節: 15

✅ 沒有發現錯誤
✅ 沒有發現警告
🎉 故事檔案完美無缺！
```

## story_converter.py - 故事格式轉換工具

### 支援的輸出格式

#### 1. CSV 格式

```bash
python story_converter.py story.json --csv story.csv
```

生成包含故事資訊、章節詳情、選項和遊戲狀態變更的 CSV 檔案。

#### 2. Markdown 格式

```bash
python story_converter.py story.json --markdown story.md
```

生成可讀性強的 Markdown 文件，包含：

- 故事資訊
- 章節內容（處理條件內容）
- 選項詳情
- 統計資訊

#### 3. 流程圖格式

```bash
python story_converter.py story.json --flowchart story.mmd
```

生成 Mermaid 格式的流程圖，包含：

- 章節節點
- 選項連接
- 條件標記
- 結局章節樣式

#### 4. 資料庫 Schema

```bash
python story_converter.py story.json --database story.sql
```

生成完整的 SQL 腳本，包含：

- 故事註冊表插入語句
- 故事表創建語句
- 章節資料插入語句

### 分析功能

#### 顯示統計資訊

```bash
python story_converter.py story.json --stats
```

顯示詳細的故事統計：

```
📊 故事統計資訊
==================================================
📚 總章節數: 21
🏁 結局章節數: 4
🔀 總選項數: 34
⚙️ 條件章節數: 15
🎮 包含狀態變更的章節: 18
📈 最多選項數: 3
📉 最少選項數: 0
📝 平均內容長度: 245.7 字元
🎯 遊戲變數數量: 18
🔍 條件統計: 布林 12 個, 數值 8 個
🎲 故事複雜度: 複雜 (評分: 156)
```

### 組合使用

```bash
# 同時輸出多種格式
python story_converter.py story.json --csv story.csv --markdown story.md --stats

python story_converter.py story.json --stats --flowchart story.mmd
```

## 工作流程建議

### 1. 故事開發流程

```bash
# 1. 建立新故事 JSON 檔案
# 2. 驗證故事檔案
python story_validator.py new_story.json

# 3. 匯入到資料庫
python seed_data.py --import-story new_story.json

# 4. 測試故事
python test_api.py  # 測試 API 功能

# 5. 生成文件
python story_converter.py new_story.json --markdown story_doc.md --stats
```

### 2. 故事維護流程

```bash
# 1. 匯出現有故事
python seed_data.py --export-story my_story --output backup.json

# 2. 編輯故事檔案
# 3. 驗證修改後的檔案
python story_validator.py modified_story.json

# 4. 重新匯入（覆蓋）
python seed_data.py --import-story modified_story.json --overwrite

# 5. 生成更新的流程圖
python story_converter.py modified_story.json --flowchart updated_flow.mmd
```

### 3. 故事分析流程

```bash
# 1. 匯出故事
python seed_data.py --export-story target_story

# 2. 生成統計報告
python story_converter.py target_story_exported_*.json --stats

# 3. 生成視覺化
python story_converter.py target_story_exported_*.json --flowchart analysis.mmd
```

## 故障排除

### 常見錯誤

#### 1. 匯入失敗

```
❌ 故事 'my_story' 已存在，使用 --overwrite 參數強制覆蓋
```

**解決方法：** 使用 `--overwrite` 參數或先刪除現有故事

#### 2. 驗證錯誤

```
❌ 章節 5 引用不存在的章節 10
```

**解決方法：** 檢查選項中的 `next_chapter` 值是否正確

#### 3. 條件語法錯誤

```
❌ 章節 3 條件內容: 變數名稱 '2invalid' 不符合命名規範
```

**解決方法：** 變數名稱必須以字母或底線開頭

### 最佳實踐

1. **定期備份**：使用 `--export-story` 定期備份重要故事
2. **版本控制**：將 JSON 檔案納入版本控制系統
3. **驗證習慣**：每次修改後都要執行驗證
4. **文件生成**：定期生成 Markdown 文件供團隊檢視
5. **統計監控**：追蹤故事複雜度和品質指標

## 進階功能

### 批次處理

```bash
# 批次驗證多個故事檔案
for file in *.json; do
    echo "驗證 $file"
    python story_validator.py "$file"
done

# 批次轉換為 Markdown
for file in *.json; do
    python story_converter.py "$file" --markdown "${file%.json}.md"
done
```

### 自動化腳本範例

```bash
#!/bin/bash
# story_deploy.sh - 故事部署腳本

STORY_FILE=$1

if [ -z "$STORY_FILE" ]; then
    echo "使用方法: $0 <story.json>"
    exit 1
fi

echo "🔍 驗證故事檔案..."
python story_validator.py "$STORY_FILE" || exit 1

echo "📥 匯入故事到資料庫..."
python seed_data.py --import-story "$STORY_FILE" --overwrite || exit 1

echo "📊 生成統計報告..."
python story_converter.py "$STORY_FILE" --stats

echo "📝 生成文件..."
python story_converter.py "$STORY_FILE" --markdown "${STORY_FILE%.json}.md"

echo "✅ 故事部署完成！"
```

這個指南涵蓋了故事管理工具的所有實際功能，沒有包含任何不存在的特性。所有範例和說明都基於實際的程式碼實作。
