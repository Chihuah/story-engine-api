# Story Engine API

**互動式冒險故事引擎 - 支援多故事管理的文字冒險遊戲系統**

[![Version](https://img.shields.io/badge/version-1.1.0-blue.svg)](https://github.com/Chihuah/story-engine-api)
[![Python](https://img.shields.io/badge/python-3.11+-green.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-red.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

## 📖 專案簡介

Story Engine API 是一個專為 ChatGPT 設計的互動式冒險故事引擎，採用現代化的 FastAPI 框架和多表資料庫架構，支援分支劇情、條件內容、遊戲狀態管理和擲骰檢定功能。

### 🎯 核心特色

- **🤖 GPT 完美整合**：專為 ChatGPT Function Calling 設計的 API 介面
- **🎭 多故事管理**：每個故事使用獨立的資料表，完全隔離，便於維護
- **📖 分支劇情系統**：玩家選擇影響故事走向，支援複雜的劇情分支
- **⚙️ 條件內容解析**：根據遊戲狀態動態顯示不同內容
- **🎲 擲骰檢定系統**：支援多面數(2-100)和多顆骰子(1-100)的檢定
- **☁️ 雲端部署就緒**：支援 Render 等平台一鍵部署

## 🚀 快速開始

### 環境需求

- Python 3.8+
- PostgreSQL 資料庫
- Git

### 安裝步驟

1. **複製專案**

   ```bash
   git clone https://github.com/Chihuah/story-engine-api.git
   cd story-engine-api
   ```

2. **建立虛擬環境**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或
   venv\Scripts\activate     # Windows
   ```

3. **安裝依賴套件**

   ```bash
   pip install -r requirements.txt
   pip install --only-binary=:all: psycopg2-binary==2.9.10
   ```

   > **注意**：如果您遇到 psycopg2-binary 編譯問題，需使用上述的 `--only-binary` 參數安裝。

4. **設定環境變數**

   ```bash
   cp .env.example .env
   # 編輯 .env 檔案，設定資料庫連線
   ```

5. **初始化資料庫**

   ```bash
   # 建立預設故事
   python seed_data.py
   ```

6. **啟動服務**

   ```bash
   uvicorn main:app --reload
   ```

7. **測試 API**
   - 開啟瀏覽器訪問 `http://localhost:8000/docs`
   - 或執行測試腳本：`python test_api.py`

## 🏗️ 系統架構

### 資料庫設計（多表架構）

```sql
-- 故事註冊表
CREATE TABLE story_registry (
    story_id VARCHAR(50) PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL UNIQUE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    author VARCHAR(255),
    version VARCHAR(50) DEFAULT '1.0',
    is_active VARCHAR(10) DEFAULT 'true',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 每個故事的獨立表格（動態建立）
CREATE TABLE story_forest_adventure (
    id INTEGER PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    options JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE story_space_odyssey (
    id INTEGER PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    options JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### API 端點架構

#### 故事管理 API

- `GET /api/stories` - 取得所有故事列表
- `GET /api/stories/{story_id}` - 取得特定故事資訊
- `GET /api/stories/{story_id}/chapters` - 取得故事章節列表
- `POST /api/stories` - 建立新故事
- `GET /api/stories/{story_id}/export` - 匯出故事為 JSON

#### 故事引擎 API

- `POST /api/story_engine/{story_id}/{chapter_id}` - 載入指定故事章節
- `POST /api/story_engine/{chapter_id}` - 載入預設故事章節（向後相容）

#### 擲骰系統 API

- `POST /api/roll_dice` - 執行擲骰檢定

## 📋 API 使用指南

### 故事引擎 API

載入故事章節內容，支援條件內容和遊戲狀態管理：

```bash
curl -X POST "http://localhost:8000/api/story_engine/forest_adventure/1" \
  -H "Content-Type: application/json" \
  -d '{
    "game_state": {
      "has_weapon": false,
      "drank_water": false,
      "health": 100
    }
  }'
```

**回應範例：**

```json
{
  "story_id": "forest_adventure",
  "story_title": "森林冒險",
  "chapter_id": 1,
  "title": "森林入口",
  "content": "你站在一片古老森林的邊緣...",
  "options": [
    { "text": "選擇平坦的小徑", "next_id": 2 },
    { "text": "選擇蜿蜒的小徑", "next_id": 3 }
  ]
}
```

### 擲骰系統 API

執行擲骰檢定，支援多面數和多顆骰子：

```bash
curl -X POST "http://localhost:8000/api/roll_dice" \
  -H "Content-Type: application/json" \
  -d '{
    "dice_count": 2,
    "dice_sides": 6,
    "modifier": 3
  }'
```

**回應範例：**

```json
{
  "dice_count": 2,
  "dice_sides": 6,
  "modifier": 3,
  "results": [4, 6],
  "total": 13,
  "description": "2D6+3 = 13"
}
```

### 故事管理 API

取得所有可用的故事列表：

```bash
curl -X GET "http://localhost:8000/api/stories"
```

**回應範例：**

```json
{
  "stories": [
    {
      "story_id": "forest_adventure",
      "table_name": "story_forest_adventure",
      "title": "森林冒險",
      "description": "一個關於勇氣與智慧的森林探險故事",
      "author": "Story Engine Team",
      "version": "1.0",
      "is_active": "true",
      "created_at": "2024-01-01T00:00:00"
    }
  ],
  "total": 1
}
```

## 🎮 遊戲狀態變數系統

### 支援的狀態類型

Story Engine 支援豐富的遊戲狀態變數，用於控制條件內容的顯示：

#### 道具狀態 (範例)

- `has_weapon` - 是否擁有武器
- `has_key` - 是否擁有鑰匙
- `has_map` - 是否擁有地圖
- `has_potion` - 是否擁有藥水

#### 行為記錄 (範例)

- `drank_water` - 是否喝過魔法井水
- `took_risk` - 是否選擇冒險行為
- `played_safe` - 是否選擇謹慎行為
- `showed_courage` - 是否展現勇氣

#### 角色屬性 (範例)

- `health` - 生命值
- `strength` - 力量值
- `wisdom` - 智慧值
- `magic_enhanced` - 是否被魔法增強

### 條件內容語法

使用 `[[IF condition]]...[[ENDIF]]` 語法來建立條件內容：

```
[[IF has_weapon]]你握緊手中的劍，準備應對可能的危險。[[ENDIF]]
[[IF NOT has_key]]門是鎖著的，你需要找到鑰匙。[[ENDIF]]
[[IF magic_enhanced]]魔法力量在你體內流淌，給了你額外的信心。[[ENDIF]]
[[IF health <= 30]]戰鬥讓你受了重傷，你感到頭暈目眩。[[ENDIF]]
```

## 🛠️ 故事管理工具

### seed_data.py - 核心管理工具

這是故事管理的核心工具，支援完整的故事生命週期管理：

#### 基本操作

```bash
# 建立預設故事
python seed_data.py

# 列出所有故事
python seed_data.py --list-stories

# 列出指定故事的章節
python seed_data.py --list-chapters forest_adventure
```

#### 匯入匯出功能

```bash
# 匯入故事（支援指定故事ID和覆蓋選項）
python seed_data.py --import-story my_story.json
python seed_data.py --import-story my_story.json --story-id custom_id --overwrite

# 匯出指定故事
python seed_data.py --export-story forest_adventure --output backup.json

# 匯出所有故事到單一檔案
python seed_data.py --export-all-stories --output all_stories.json
```

#### 清理功能

```bash
# 刪除指定故事
python seed_data.py --clear-story forest_adventure

# 刪除所有故事（需要確認）
python seed_data.py --clear-all
```

### 故事驗證和轉換工具

#### story_validator.py - 故事驗證工具

```bash
# 驗證故事檔案的完整性和邏輯
python story_validator.py my_story.json
```

驗證項目包括：

- 基本結構和必要欄位檢查
- 章節引用完整性驗證
- 邏輯結構分析（起始章節、結局章節、孤立章節）
- 條件語法正確性檢查
- 內容品質評估

#### story_converter.py - 格式轉換工具

```bash
# 轉換為可讀的 Markdown 文件
python story_converter.py story.json --markdown story.md

# 生成視覺化流程圖
python story_converter.py story.json --flowchart story.mmd

# 轉換為 CSV 表格格式
python story_converter.py story.json --csv story.csv

# 顯示詳細統計資訊
python story_converter.py story.json --stats
```

**詳細使用指南：** 請參考 [STORY_MANAGEMENT.md](STORY_MANAGEMENT.md)

## 📁 專案結構

```
story-engine-api/
├── 📋 核心程式檔案
│   ├── main.py                    # FastAPI 主程式
│   ├── models.py                  # 資料庫模型（多表設計）
│   └── schemas.py                 # API 請求與回應的資料結構
│
├── 🛠️ 故事管理工具
│   ├── seed_data.py               # 故事資料管理工具（匯入/匯出/清除/列表）
│   ├── story_validator.py         # 故事檔案驗證工具
│   ├── story_converter.py         # 故事格式轉換工具
│   ├── migration_to_multi_table.py # 資料庫遷移腳本
│   ├── example_simple_story.json  # 簡單故事範例檔案
│   └── example_enhanced_story.json # 稍加完整的故事範例檔案
│
├── 🧪 測試檔案
│   ├── test_api.py                # 測試 API 功能的腳本
│   └── test_db_connection.py      # 測試資料庫連線的腳本
│
├── ⚙️ 配置檔案
│   ├── requirements.txt           # Python 套件需求清單
│   ├── Procfile                   # Render 平台的部署配置檔案
│   ├── .env.example               # 環境變數設定範例檔案
│   └── .gitignore                 # Git 版本控制忽略檔案
│
├── 🤖 GPT 整合檔案
│   ├── gpt_tools_definition.json  # 定義 GPT 工具的 JSON 檔案
│   ├── GPT_INTEGRATION.md         # GPT 整合指南文件
│   └── GPT_ACTION_OPTIMIZATION.md # GPT Action 優化指南文件
│
├── 🌐 隱私權政策
│   └── privacy-policy.html        # 完整的隱私權政策頁面
│
└── 📚 文件檔案
    ├── README.md                  # 專案的主要說明文件
    ├── DEPLOYMENT.md              # 部署指南文件
    ├── LOCAL_DEVELOPMENT.md       # 本地開發環境設定指南
    ├── STORY_MANAGEMENT.md        # 故事管理完整指南
    ├── AI_STORY_CREATION_GUIDE.md # AI 故事創作指南
    ├── PRIVACY_POLICY_SETUP.md    # 隱私權政策部署說明
    └── LICENSE                    # MIT 開源授權條款
```

## 📖 故事內容

### 範例故事：「森林冒險」

本專案提供一個簡單的範例故事（`example_simple_story.json`）：

- **21 個章節**：森林探險主題
- **多重結局（7 個）**：每個結局都反映不同的遊戲狀態
- **條件內容**：使用 `[[IF condition]]...[[ENDIF]]` 語法，展示裝備狀態影響或玩家行為後果等
- **分支設計**：玩家選擇真正影響故事走向
- **狀態追蹤**：展示遊戲狀態變數的使用

### 故事結構

```mermaid
flowchart TD
    1["森林入口"] -- 沿著寬闊的主要小徑前進 --> 2["主要小徑"]
    1 -- 選擇神秘的側路探索 --> 3["神秘側路"]
    2 -- 喝一些井水補充體力 --> 4["清涼的井水"]
    2 -- 嘗試打開木箱 --> 5["神秘的木箱"]
    3 -- 仔細研究地圖並收起來 --> 6["寶藏地圖的秘密"]
    3 -- 立即離開這個危險的地方 --> 7["謹慎的撤退"]
    4 -- 冒險下井取得金幣 --> 8["勇敢的收穫"]
    4 -- 安全起見，繼續前進 --> 9["安全的選擇"]
    5 -- 喝下神秘藥水 --> 10["魔法的力量"]
    5 -- 保存藥水，繼續探索 --> 11["謹慎的準備"]
    6 -- 按照地圖走安全路線 --> 12["安全路線的智慧"]
    6 -- 直接朝寶藏位置前進 --> 13["直接路線的挑戰"]
    7 -- 沿著隱蔽小徑前進 --> 14["隱蔽小徑的發現"]
    7 -- 回到森林入口重新選擇 --> 1
    8 -- 繼續深入森林尋找更多寶藏 --> 15["寶藏獵人的結局"]
    9 -- 跟隨腳印探索 --> 16["追蹤者的發現"]
    10 -- 朝號角聲的方向前進 --> 17["守護者的召喚"]
    11 -- 朝音樂聲的方向前進 --> 18["音樂的魔法"]
    12 -- 小心地接近水晶球 --> 19["智慧的寶藏"]
    13 -- 展示你的勇氣，直面森林狼 --> 20["勇者的認可"]
    14 -- 接受精靈的祝福 --> 21["精靈的祝福"]
     15:::ending
     16:::ending
     17:::ending
     18:::ending
     19:::ending
     20:::ending
     21:::ending
    classDef ending fill:#ffcccc,stroke:#ff6666,stroke-width:2px
```

- 另有一個較完整的互動式劇本（`example_enhanced_story.json`）亦可參考

### 管理故事內容

1. **使用現有故事**：

   ```bash
   python seed_data.py --import example_simple_story.json  # 載入範例故事
   ```

2. **使用自創故事**：

   ```bash
   python seed_data.py --export my_story.json   # 匯出模板
   # 編輯 my_story.json
   python story_validator.py my_story.json      # 驗證故事
   python seed_data.py --import my_story.json   # 匯入新故事
   ```

3. **管理和轉換**：
   ```bash
   python seed_data.py --list                   # 查看所有章節
   python story_converter.py story.json --stats # 查看統計
   python story_converter.py story.json --flowchart story.mmd  # 生成流程圖
   ```

### 自創故事

#### 利用 AI 來創作互動式冒險故事

可利用 [AI_STORY_CREATION_GUIDE.md](AI_STORY_CREATION_GUIDE.md) 此故事生成指引（提示詞/上下文脈絡），給予大型語言模型來創作。並且搭配 [example_simple_story.json](example_simple_story.json) 做為範例，使其生成符合本專案的 json 格式。自創故事可用上述管理工具驗證後匯入至資料庫。

## 🤖 GPT 整合

### 設定自訂 GPT

詳細的整合指南請參考 [GPT_INTEGRATION.md](GPT_INTEGRATION.md)

**主要步驟：**

1. 建立自訂 GPT
2. 設定 Instructions（遊戲主持人指示）
3. 新增 Actions（API 工具）
4. 測試功能
5. 發布 GPT

### Function Calling 工具定義

工具定義檔案：[gpt_tools_definition.json](gpt_tools_definition.json)

Story Engine API 提供完整的 GPT Function Calling 支援，包含以下工具：

#### 故事管理工具

- `list_available_stories()` - 取得所有可用故事列表
- `get_story_info(story_id)` - 取得特定故事詳細資訊
- `get_story_chapters(story_id)` - 取得故事章節列表

#### 遊戲核心工具

- `get_story_chapter(story_id, chapter_id, game_state)` - 載入章節內容
- `roll_dice(dice_count, dice_sides, modifier)` - 執行擲骰檢定

#### 管理工具

- `export_story(story_id)` - 匯出故事為 JSON 格式

### GPT 使用流程

1. **開始遊戲**

   ```
   GPT: 歡迎來到互動式冒險故事世界！
   [呼叫 list_available_stories()]

   請選擇您想要體驗的故事：
   1. 🌲 森林冒險 - 關於勇氣與智慧的探險故事
   2. 🚀 太空奧德賽 - 浩瀚宇宙中的科幻冒險
   ```

2. **遊戲進行**

   ```
   玩家: 我想玩森林冒險

   GPT: [呼叫 get_story_chapter("forest_adventure", 1, {})]

   你站在一片古老森林的邊緣...
   你想要：
   1. 選擇平坦的小徑
   2. 選擇蜿蜒的小徑
   ```

3. **狀態管理**

   ```
   玩家: 我選擇蜿蜒的小徑

   GPT: [呼叫 get_story_chapter("forest_adventure", 3, {
     "took_risk": true,
     "played_safe": false
   })]

   蜿蜒的小徑帶你來到一個小空地...
   你的冒險精神得到了回報。
   ```

4. **擲骰檢定**

   ```
   GPT: 你需要進行一次敏捷檢定來避開陷阱
   [呼叫 roll_dice(1, 20, 2)]

   你擲出了 1D20+2 = 15
   成功！你敏捷地避開了陷阱。
   ```

### GPT Instructions 簡易範例

```
你是一位專業的互動式冒險故事遊戲主持人。你的任務是：

1. 使用 story_engine 工具載入故事章節
2. 向玩家生動地描述當前情境
3. 清楚地展示所有可選擇的行動選項
4. 當需要隨機判定時使用 roll_dice 工具
5. 追蹤玩家的遊戲狀態

記住：創造引人入勝、互動性強的冒險體驗！
```

### 🔧 減少確認提示（重要優化）

為了提升對話流暢性，我們已經在 API 中添加了 `x-openai-isConsequential: false` 標記。

**使用步驟：**

1. 重新部署包含優化的 API 程式碼
2. 在 GPT Action 中更新 API schema
3. 首次使用時點擊「Always Allow」
4. 後續 API 呼叫將不再需要確認

詳細說明請參考 [GPT_ACTION_OPTIMIZATION.md](GPT_ACTION_OPTIMIZATION.md)

## 🚀 部署指南

### 本地部署測試

用於測試的本地部署，步驟請參考 [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md)

### Render 平台部署（推薦）

詳細的 Render 平台部署，步驟請參考 [DEPLOYMENT.md](DEPLOYMENT.md)

**快速部署步驟：**

1. 將程式碼推送到 GitHub
2. 在 Render 建立 Web Service
3. 新增 PostgreSQL 資料庫
4. 設定環境變數
5. 執行資料庫初始化

### 環境變數設定

```bash
DATABASE_URL=postgresql://username:password@hostname:5432/database_name
PORT=8000
DEBUG=False
```

## 🧪 測試

### API 呼叫範例

```python
import requests

# 載入故事章節
response = requests.post("https://your-api.onrender.com/story_engine",
    json={"chapter_id": 1})
story_data = response.json()

# 執行擲骰檢定
response = requests.post("https://your-api.onrender.com/roll_dice",
    json={"dice_sides": 20, "dice_count": 1})
dice_result = response.json()
```

### API 功能測試

```bash
# 執行完整的 API 測試
python test_api.py

# 測試資料庫連線
python test_db_connection.py
```

### 手動測試

1. **測試故事引擎**

   ```bash
   curl -X POST "https://your-api.onrender.com/story_engine/forest_adventure/1" \
     -H "Content-Type: application/json" \
     -d '{"game_state": {}}'
   ```

2. **測試擲骰系統**

   ```bash
   curl -X POST "https://your-api.onrender.com/roll_dice" \
     -H "Content-Type: application/json" \
     -d '{"dice_count": 2, "dice_sides": 6, "modifier": 0}'
   ```

3. **測試故事管理**
   ```bash
   curl -X GET "https://your-api.onrender.com/stories"
   ```

## 🔧 故障排除

### 除錯工具

1. **查看 API 文件**

   - 訪問 `https://your-api.onrender.com/docs`

2. **檢查日誌**

   ```bash
   # 啟動時顯示詳細日誌
   uvicorn main:app --reload --log-level debug
   ```

3. **驗證故事檔案**
   ```bash
   python story_validator.py your_story.json
   ```

## 📚 進階功能

### 自訂故事建立

自訂故事建立之細節，詳見 [AI_STORY_CREATION_GUIDE.md](AI_STORY_CREATION_GUIDE.md) 創作指南

#### 1. 故事結構設計

```json
{
  "story_id": "my_adventure",
  "title": "我的冒險",
  "description": "一個精彩的冒險故事",
  "author": "作者名稱",
  "chapters": [
    {
      "id": 1,
      "title": "開始",
      "content": "故事內容...",
      "options": [
        {
          "text": "選項文字",
          "next_id": 2,
          "game_state": { "key": "value" }
        }
      ]
    }
  ]
}
```

#### 2. 條件內容設計

```
基本語法：[[IF condition]]內容[[ENDIF]]
NOT 語法：[[IF NOT condition]]內容[[ENDIF]]
條件語法：[[IF wisdom >= 15]]內容[[ENDIF]]

範例：
[[IF has_sword]]你握著鋒利的劍。[[ENDIF]]
[[IF NOT has_key]]門是鎖著的。[[ENDIF]]
[[IF wisdom >= 15]]智者看出了你的潛力，決定傳授你更深奧的知識。[[ENDIF]]
[[IF wisdom < 15]]智者認為你還需要更多的學習和思考。[[ENDIF]]
```

#### 3. 遊戲狀態設計

- 使用有意義的變數名稱
- 保持狀態的一致性
- 考慮狀態之間的邏輯關係
- 適當使用布林值和數值

## 🔧 技術規格

### 後端技術

- **FastAPI**：現代化的 Python Web 框架
- **SQLAlchemy**：Python SQL 工具包和 ORM
- **PostgreSQL**：關聯式資料庫
- **Pydantic**：資料驗證和設定管理
- **Uvicorn**：ASGI 伺服器

### API 規格

- **RESTful API**：遵循 REST 設計原則
- **OpenAPI 3.0**：自動生成 API 文件
- **JSON 格式**：統一的資料交換格式
- **CORS 支援**：跨域請求支援
- **錯誤處理**：統一的錯誤回應格式

## 🔮 未來規劃

### 短期目標

- [x] 後端資料庫收錄多本故事劇情，提供玩家選擇切換
- [ ] 新增更多故事情節內容和分支(AI 輔助故事生成，使用自創故事指引來創作)
- [ ] 實作角色屬性和道具系統
- [ ] 加入戰鬥機制和技能檢定
- [ ] 實作玩家進度儲存

### 中期目標

- [ ] 支援多語言內容
- [ ] 開發故事編輯器介面
- [ ] 新增（由 AI 生成的）圖片、語音與音效支援
- [ ] 建立故事分享社群

### 長期目標

- [ ] 多人協作冒險模式
- [ ] 行動應用程式版本
- [ ] 虛擬實境整合

## 📄 授權條款

本專案採用 MIT 授權條款。詳細內容請參考 [LICENSE](LICENSE) 檔案。

## 🙏 致謝

- **FastAPI**：提供優秀的 Python Web 框架
- **SQLAlchemy**：強大的 Python ORM 工具
- **Render**：便利的雲端部署平台
- **OpenAI**：GPT 技術和 Function Calling 功能
- **AI Agent**：Manus AI

---

**開始您的冒險之旅吧！** 🗡️⚔️🛡️
