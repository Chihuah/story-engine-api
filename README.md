# GPTs 互動式冒險故事引擎

一個專為 GPTs 系統設計的互動式冒險故事引擎，支援透過 PostgreSQL 儲存結構化劇情章節，並由 GPT 透過兩個功能 API（`story_engine` 與 `roll_dice`）互動呼叫，進行章節導向與擲骰檢定。

## 🎯 專案特色

- **🤖 GPT 整合**：專為 ChatGPT Function Calling 設計的 API 介面
- **📚 故事引擎**：支援分支劇情、條件內容和遊戲狀態管理
- **🎲 擲骰系統**：多面數、多顆骰子的隨機檢定機制
- **🗄️ 資料庫儲存**：使用 PostgreSQL 儲存故事章節和選項
- **☁️ 雲端部署**：支援 Render 平台一鍵部署
- **🔧 易於擴展**：模組化設計，方便新增更多故事內容

## 🏗️ 系統架構

```
GPTs 自訂模型 ──┐
                ├─→ FastAPI Server ──→ PostgreSQL
開發者工具 ─────┘
```

- **GPTs**：透過 Function Calling 呼叫 API
- **FastAPI**：提供 RESTful API 服務
- **PostgreSQL**：儲存故事章節與選項資料
- **Render**：雲端部署平台

## 📋 功能說明

### 1. Story Engine API (`/story_engine`)

載入故事章節內容與選項，支援遊戲狀態條件解析。

**功能特點：**

- 根據章節 ID 載入完整內容
- 支援 `[[IF condition]]...[[ENDIF]]` 條件內容
- 返回可選擇的行動選項
- 遊戲狀態變數管理

**請求範例：**

```json
{
  "chapter_id": 2,
  "game_state": {
    "health": 60,
    "drank_water": false
  }
}
```

**回應範例：**

```json
{
  "id": 2,
  "title": "主要小徑",
  "content": "你沿著寬闊的小徑深入森林，陽光透過樹葉... ...井水看起來清澈見底，而木箱則散發著歲月的氣息。\n\n[[IF has_weapon]]你握緊手中的劍，準備應對可能的危險。[[ENDIF]]\n\n你注意到木箱上有一把簡單的鎖，但看起來並不牢固。",
  "options": [
    {
      "text": "喝一些井水補充體力",
      "next_id": 4,
      "game_state": {
        "health": 120,
        "drank_water": true
      }
    },
    {
      "text": "嘗試打開木箱",
      "next_id": 5,
      "game_state": {
        "opened_chest": true
      }
    }
  ]
}
```

### 2. Roll Dice API (`/roll_dice`)

執行擲骰子檢定，支援多面數與多顆骰子。

**功能特點：**

- 支援 2-100 面骰子
- 可同時擲 1-100 顆骰子
- 返回個別結果和總和
- 自動生成描述文字

**請求範例：**

```json
{
  "dice_sides": 20,
  "dice_count": 1
}
```

**回應範例：**

```json
{
  "rolls": [15],
  "total": 15,
  "description": "1D20 擲出的結果"
}
```

### 3. 故事管理系統

完整的故事內容管理工具集，支援故事的建立、編輯、驗證和轉換。

**核心工具：**

#### `seed_data.py` - 故事資料管理

```bash
python seed_data.py                          # 載入預設故事
python seed_data.py --import story.json      # 匯入故事檔案
python seed_data.py --export story.json      # 匯出故事檔案
python seed_data.py --export-db backup.json  # 從資料庫匯出
python seed_data.py --list                   # 列出所有章節
python seed_data.py --clear                  # 清除所有資料
```

#### `story_validator.py` - 故事驗證

```bash
python story_validator.py story.json         # 驗證故事檔案
```

驗證項目：

- ✅ 基本結構和必要欄位
- 🔗 章節引用完整性
- 🧠 邏輯結構（起始章節、結局章節、孤立章節）
- ⚙️ 條件語法正確性
- 📝 內容品質檢查

#### `story_converter.py` - 格式轉換

```bash
python story_converter.py story.json --csv story.csv           # 轉為 CSV
python story_converter.py story.json --markdown story.md       # 轉為 Markdown
python story_converter.py story.json --flowchart story.mmd     # 轉為流程圖
python story_converter.py story.json --stats                   # 顯示統計
```

**故事檔案格式：**

```json
[
  {
    "id": 1,
    "title": "章節標題",
    "content": "章節內容...\n\n[[IF condition]]\n條件內容\n[[ENDIF]]",
    "options": [
      {
        "text": "選項文字",
        "next_id": 2
      }
    ]
  }
]
```

**詳細使用指南：** 請參考 [STORY_MANAGEMENT.md](STORY_MANAGEMENT.md)

## 🚀 快速開始

### 前置需求

- Python 3.8+
- PostgreSQL 資料庫
- Git

### 本地開發設定

1. **複製專案**

   ```bash
   git clone https://github.com/yourusername/story-engine-api.git
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

   # 單獨安裝 psycopg2-binary（避免編譯問題）
   pip install --only-binary=:all: psycopg2-binary==2.9.10
   ```

   > **注意**：如果您遇到 Pydantic 安裝問題（需要 Rust），requirements.txt 已使用相容版本 1.10.13。
   > 如果您遇到 psycopg2-binary 編譯問題，請使用上述的 `--only-binary` 參數安裝。

4. **設定環境變數**

   ```bash
   cp .env.example .env
   # 編輯 .env 檔案，設定資料庫連線資訊
   ```

5. **初始化資料庫**

   ```bash
   python seed_data.py
   ```

6. **啟動開發伺服器**

   ```bash
   uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ```

7. **測試 API**
   ```bash
   python test_api.py
   ```

### 訪問 API 文件

啟動伺服器後，可以透過以下網址訪問：

- **API 文件**：http://localhost:8000/docs
- **健康檢查**：http://localhost:8000/health
- **根路徑**：http://localhost:8000/

## 📦 部署指南

### 本地部署測試

用於測試的本地部署，步驟請參考 [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md)

### Render 雲端部署

詳細的部署步驟請參考 [DEPLOYMENT.md](DEPLOYMENT.md)

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

## 🤖 GPT 整合

### 設定自訂 GPT

詳細的整合指南請參考 [GPT_INTEGRATION.md](GPT_INTEGRATION.md)

**主要步驟：**

1. 建立自訂 GPT
2. 設定 Instructions（遊戲主持人指示）
3. 新增 Actions（API 工具）
4. 測試功能
5. 發布 GPT

### GPT Instructions 範例

```
你是一位專業的互動式冒險故事遊戲主持人。你的任務是：

1. 使用 story_engine 工具載入故事章節
2. 向玩家生動地描述當前情境
3. 清楚地展示所有可選擇的行動選項
4. 當需要隨機判定時使用 roll_dice 工具
5. 追蹤玩家的遊戲狀態

記住：創造引人入勝、互動性強的冒險體驗！
```

### Function Tools 定義

工具定義檔案：[gpt_tools_definition.json](gpt_tools_definition.json)

## 📖 故事內容

### 範例故事：「森林冒險」

本專案提供一個簡單的範例故事（`example_simple_story.json`）：

- **21 個章節**：森林探險主題
- **多重結局（7 個）**：每個結局都反映不同的遊戲狀態
- **條件內容**：使用 `[[IF condition]]...[[ENDIF]]` 語法，展示裝備狀態影響或玩家行為後果等
- **分支設計**：玩家選擇真正影響故事走向
- **狀態追蹤**：展示遊戲狀態變數的使用

### 故事結構

<img src="ExampleSimpleStoryMermaidChart.svg" width="75%">

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

## 🧪 測試

### 自動化測試

```bash
# 執行 API 測試
python test_api.py

# 測試資料庫連線
python -c "from models import create_tables; create_tables()"
```

### 手動測試

使用 FastAPI 自動生成的文件介面：
http://localhost:8000/docs

### 測試案例

- ✅ 載入存在的章節
- ✅ 載入不存在的章節（錯誤處理）
- ✅ 帶入遊戲狀態的條件內容
- ✅ 各種骰子組合的擲骰
- ✅ 無效參數的錯誤處理

## 📁 專案結構

```
project/
├── 📋 核心程式檔案
│   ├── main.py                    # FastAPI 主程式
│   ├── models.py                  # 定義資料庫模型的 SQLAlchemy 程式碼
│   └── schemas.py                 # 定義 API 請求與回應的 Pydantic 資料結構
│
├── 🛠️ 故事管理工具
│   ├── seed_data.py               # 故事資料管理工具（匯入/匯出/清除/列表）
│   ├── story_validator.py         # 故事檔案驗證工具，檢查完整性和邏輯
│   ├── story_converter.py         # 格式轉換工具，支援 CSV、Markdown、流程圖輸出
│   └── example_simple_story.json  # 包含分支劇情和條件內容的範例故事
│
├── 🧪 測試檔案
│   ├── test_api.py                # 測試 API 功能的腳本
│   └── test_db_connection.py      # 測試資料庫連線的腳本
│
├── ⚙️ 配置檔案
│   ├── requirements.txt           # Python 套件需求清單
│   ├── Procfile                   # Render 平台的部署配置檔案
│   └── .env.example               # 環境變數設定範例檔案
│
├── 🤖 GPT 整合檔案
│   ├── gpt_tools_definition.json  # 定義 GPT 工具的 JSON 檔案
│   └── GPT_INTEGRATION.md         # GPT 整合指南文件
│
└── 📚 文件檔案
    ├── README.md                  # 專案的主要說明文件
    ├── DEPLOYMENT.md              # 部署指南文件
    ├── LOCAL_DEVELOPMENT.md       # 本地開發環境設定指南
    ├── STORY_MANAGEMENT.md        # 故事管理完整指南
    └── LICENSE                    # MIT 開源授權條款
```

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

### 資料庫設計

```sql
CREATE TABLE story_chapters (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    options TEXT,  -- JSON 格式
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🎮 使用範例

### 基本遊戲流程

1. **開始遊戲**

   ```
   玩家：「我想開始一個新的冒險故事」
   GPT：載入第 1 章，描述開端情境
   ```

2. **玩家選擇**

   ```
   玩家：「我選擇第一個選項」
   GPT：載入對應章節，繼續故事
   ```

3. **擲骰檢定**

   ```
   玩家：「我想嘗試潛行」
   GPT：執行 D20 檢定，根據結果決定劇情
   ```

4. **狀態管理**
   ```
   GPT：追蹤玩家獲得的道具和觸發的事件
   在載入章節時傳遞遊戲狀態
   ```

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

## 🔮 未來規劃

### 短期目標

- [ ] 新增更多故事情節內容和分支(AI 輔助故事生成，使用自創故事指引來創作)
- [ ] 實作角色屬性和道具系統
- [ ] 加入戰鬥機制和技能檢定
- [ ] 實作玩家進度儲存
- [ ] 後端資料庫收錄多本故事劇情，提供玩家選擇切換

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
