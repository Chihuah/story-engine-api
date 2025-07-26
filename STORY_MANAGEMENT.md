# 故事管理指南

本指南詳細說明如何使用增強版的故事管理工具來建立、編輯、驗證和轉換故事內容。

## 📖 概述

故事引擎支援 JSON 格式的故事檔案，您可以：

- 📥 **匯入故事**：從 JSON 檔案載入故事到資料庫
- 📤 **匯出故事**：將資料庫中的故事匯出為 JSON 檔案
- ✅ **驗證故事**：檢查故事檔案的完整性和邏輯
- 🔄 **轉換格式**：將故事轉換為不同格式（CSV、Markdown、流程圖）
- 📊 **分析統計**：查看故事的統計資訊

## 🛠️ 工具介紹

### 1. seed_data.py - 故事資料管理工具

這是主要的故事管理工具，支援多種操作模式：

```bash
# 基本用法
python seed_data.py                          # 載入預設故事資料
python seed_data.py --import story.json      # 從 JSON 檔案匯入故事
python seed_data.py --export story.json      # 匯出預設故事到 JSON 檔案
python seed_data.py --export-db story.json   # 從資料庫匯出到 JSON 檔案
python seed_data.py --clear                  # 清除所有章節
python seed_data.py --list                   # 列出所有章節
```

### 2. story_validator.py - 故事驗證工具

用於檢查故事檔案的完整性：

```bash
python story_validator.py story.json              # 驗證故事檔案
python story_validator.py example_simple_story.json  # 驗證範例故事
```

### 3. story_converter.py - 故事格式轉換工具

支援多種輸出格式：

```bash
python story_converter.py story.json --csv story.csv           # 轉換為 CSV
python story_converter.py story.json --markdown story.md       # 轉換為 Markdown
python story_converter.py story.json --flowchart story.mmd     # 轉換為流程圖
python story_converter.py story.json --stats                   # 顯示統計資訊
```

## 📋 故事檔案格式

### JSON 格式規範

故事檔案必須是包含章節陣列的 JSON 檔案：

```json
[
  {
    "id": 1,
    "title": "章節標題",
    "content": "章節內容...",
    "options": [
      {
        "text": "選項文字",
        "next_id": 2
      }
    ]
  }
]
```

### 必要欄位

每個章節必須包含以下欄位：

- **id** (整數)：章節的唯一識別碼
- **title** (字串)：章節標題
- **content** (字串)：章節內容
- **options** (陣列)：選項列表，結局章節可以是空陣列

### 選項格式

每個選項必須包含：

- **text** (字串)：選項顯示文字
- **next_id** (整數)：指向下一個章節的 ID

### 條件內容語法

支援條件顯示內容：

```
[[IF condition_name]]
這段內容只有在 condition_name 為 true 時才會顯示
[[ENDIF]]
```

## 🚀 快速開始

### 1. 建立新故事

#### 方法一：從範例開始

```bash
# 複製範例故事檔案
cp example_simple_story.json my_story.json

# 編輯故事內容
nano my_story.json  # 或使用您喜歡的編輯器

# 驗證故事檔案
python story_validator.py my_story.json

# 匯入到資料庫
python seed_data.py --import my_story.json
```

#### 方法二：匯出現有故事修改

```bash
# 匯出預設故事
python seed_data.py --export my_story.json

# 編輯故事內容
nano my_story.json

# 重新匯入
python seed_data.py --clear
python seed_data.py --import my_story.json
```

### 2. 驗證故事

在匯入故事之前，建議先驗證：

```bash
python story_validator.py my_story.json
```

驗證工具會檢查：

- ✅ **基本結構**：必要欄位、資料類型
- 🔗 **章節引用**：確保所有 next_id 都指向存在的章節
- 🧠 **邏輯結構**：檢查起始章節、結局章節、孤立章節
- ⚙️ **條件語法**：驗證 IF/ENDIF 語法
- 📝 **內容品質**：檢查標題長度、內容長度、選項數量

### 3. 管理故事資料

#### 查看現有章節

```bash
python seed_data.py --list
```

#### 清除所有資料

```bash
python seed_data.py --clear
```

#### 備份故事資料

```bash
python seed_data.py --export-db backup_$(date +%Y%m%d).json
```

### 4. 轉換和分析

#### 生成可讀的 Markdown 文件

```bash
python story_converter.py my_story.json --markdown story_readable.md
```

#### 生成流程圖

```bash
python story_converter.py my_story.json --flowchart story_flowchart.mmd
```

您可以將 `.mmd` 檔案貼到 [Mermaid Live Editor](https://mermaid.live/) 來查看視覺化流程圖。

#### 查看統計資訊

```bash
python story_converter.py my_story.json --stats
```

## 📝 故事編寫最佳實踐

### 1. 章節設計

#### 章節 ID 規劃

- 使用連續的整數 ID（1, 2, 3...）
- 起始章節建議使用 ID 1
- 為未來擴展預留 ID 空間

#### 標題命名

- 保持簡潔明瞭（建議 50 字元以內）
- 反映章節的主要內容或場景
- 避免劇透重要情節

#### 內容撰寫

- 每章內容建議 100-2000 字元
- 使用生動的描述營造氛圍
- 在章節結尾提供明確的選擇提示

### 2. 選項設計

#### 選項數量

- 建議每章 2-5 個選項
- 避免只有一個選項（除非有特殊劇情需要）
- 太多選項會讓玩家感到困惑

#### 選項文字

- 清楚描述行動或決定
- 避免過於模糊的表述
- 長度適中，避免過長

### 3. 故事結構

#### 分支設計

- 確保每個分支都有意義
- 避免「假選擇」（所有選項都導向同一結果）
- 設計多個不同的結局

#### 條件使用

- 合理使用條件內容增加重玩價值
- 條件變數命名要有意義（如 `has_key`、`found_secret`）
- 避免過於複雜的條件邏輯

### 4. 測試和除錯

#### 完整測試

- 測試每個可能的路徑
- 確保所有結局都可達到
- 檢查條件內容是否正確顯示

#### 使用驗證工具

```bash
# 定期驗證故事檔案
python story_validator.py my_story.json

# 查看故事統計
python story_converter.py my_story.json --stats

# 生成流程圖檢查邏輯
python story_converter.py my_story.json --flowchart check.mmd
```

## 🔧 進階功能

### 1. 批次操作

#### 批次匯入多個故事

```bash
# 建立批次匯入腳本
for file in stories/*.json; do
    echo "匯入 $file"
    python seed_data.py --clear
    python seed_data.py --import "$file"
    # 執行測試或其他操作
done
```

#### 批次驗證

```bash
# 驗證所有故事檔案
for file in stories/*.json; do
    echo "驗證 $file"
    python story_validator.py "$file"
done
```

### 2. 版本控制

#### Git 整合

```bash
# 初始化 Git 倉庫
git init story-project
cd story-project

# 加入故事檔案
git add *.json
git commit -m "初始故事版本"

# 建立分支進行實驗
git checkout -b experimental-ending
# 修改故事...
git add my_story.json
git commit -m "新增實驗性結局"

# 合併回主分支
git checkout main
git merge experimental-ending
```

#### 版本標記

```bash
# 為穩定版本建立標籤
git tag -a v1.0 -m "故事版本 1.0"
git tag -a v1.1 -m "故事版本 1.1 - 修復錯字"
```

### 3. 自動化工作流程

#### 建立 Makefile

```makefile
# Makefile
.PHONY: validate import export clean test

validate:
	python story_validator.py story.json

import: validate
	python seed_data.py --clear
	python seed_data.py --import story.json

export:
	python seed_data.py --export-db story_backup.json

clean:
	python seed_data.py --clear

test: import
	python test_api.py

docs:
	python story_converter.py story.json --markdown story.md
	python story_converter.py story.json --flowchart story.mmd

all: validate import test docs
```

使用方式：

```bash
make validate  # 驗證故事
make import    # 匯入故事
make test      # 執行測試
make docs      # 生成文件
make all       # 執行所有步驟
```

## 🐛 常見問題和解決方案

### 1. 驗證錯誤

#### 「章節 ID 重複」

**問題**：多個章節使用相同的 ID

**解決方案**：

```bash
# 檢查重複 ID
grep -o '"id": [0-9]*' story.json | sort | uniq -d

# 手動修正或使用工具重新編號
```

#### 「引用不存在的章節」

**問題**：選項的 next_id 指向不存在的章節

**解決方案**：

```bash
# 檢查所有引用
python story_validator.py story.json

# 查看詳細的引用關係
python story_converter.py story.json --stats
```

### 2. 匯入問題

#### 「JSON 格式錯誤」

**問題**：JSON 語法不正確

**解決方案**：

```bash
# 使用 JSON 驗證工具
python -m json.tool story.json

# 或使用線上工具：https://jsonlint.com/
```

#### 「資料庫連線失敗」

**問題**：無法連接到資料庫

**解決方案**：

```bash
# 檢查資料庫連線
python test_db_connection.py

# 檢查環境變數
echo $DATABASE_URL
```

### 3. 效能問題

#### 大型故事檔案處理緩慢

**解決方案**：

- 將大型故事分割成多個檔案
- 使用批次處理
- 考慮使用資料庫索引

#### 記憶體使用過多

**解決方案**：

- 分批處理章節
- 使用串流處理大型檔案
- 定期清理暫存資料

## 📚 範例和模板

### 1. 簡單線性故事

```json
[
  {
    "id": 1,
    "title": "開始",
    "content": "故事開始...",
    "options": [{ "text": "繼續", "next_id": 2 }]
  },
  {
    "id": 2,
    "title": "中間",
    "content": "故事發展...",
    "options": [{ "text": "繼續", "next_id": 3 }]
  },
  {
    "id": 3,
    "title": "結局",
    "content": "故事結束。",
    "options": []
  }
]
```

### 2. 分支故事

```json
[
  {
    "id": 1,
    "title": "選擇",
    "content": "你面臨一個選擇...",
    "options": [
      { "text": "選擇 A", "next_id": 2 },
      { "text": "選擇 B", "next_id": 3 }
    ]
  },
  {
    "id": 2,
    "title": "結局 A",
    "content": "你選擇了 A，結果是...",
    "options": []
  },
  {
    "id": 3,
    "title": "結局 B",
    "content": "你選擇了 B，結果是...",
    "options": []
  }
]
```

### 3. 條件內容故事

```json
[
  {
    "id": 1,
    "title": "探索",
    "content": "你在房間裡搜索。\n\n[[IF found_key]]\n你已經找到了鑰匙。\n[[ENDIF]]",
    "options": [
      { "text": "檢查桌子", "next_id": 2 },
      { "text": "離開房間", "next_id": 3 }
    ]
  }
]
```

## 🔮 未來擴展

### 計劃中的功能

1. **視覺化編輯器**：圖形化的故事編輯界面
2. **多媒體支援**：圖片、音效、背景音樂
3. **進階條件系統**：數值變數、複雜邏輯
4. **多語言支援**：國際化和本地化
5. **協作編輯**：多人同時編輯故事
6. **版本比較**：視覺化的版本差異比較

### 社群貢獻

歡迎貢獻：

- 🐛 回報錯誤
- 💡 提出功能建議
- 📝 改善文件
- 🔧 提交程式碼修正
- 📖 分享故事範例

---

## 📞 支援和協助

如果您在使用過程中遇到問題：

1. 查看本指南的常見問題部分
2. 使用驗證工具檢查故事檔案
3. 查看錯誤訊息和日誌
4. 參考範例檔案和模板

希望這份指南能幫助您創作出精彩的互動式故事！
