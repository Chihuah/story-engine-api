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
    "found_secret_path": true,
    "has_key": false
  }
}
```

**回應範例：**

```json
{
  "chapter_id": 2,
  "title": "找人聊聊",
  "content": "你們決定先去宮裡的人間清楚前因後果...",
  "options": [
    {
      "text": "研究詛咒的解除方法",
      "next_id": 4
    },
    {
      "text": "尋找歐司崔特的把柄",
      "next_id": 5
    }
  ],
  "game_state": {
    "found_secret_path": true,
    "has_key": false
  }
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
   ```

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
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
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

### 預設故事：「詛咒公主」

專案包含一個完整的範例故事，改編自經典的奇幻冒險劇情：

- **7 個章節**：包含開端、分支和 4 個不同結局
- **多重結局**：魔法解咒、政治勒索、人性和解、黑暗終結
- **條件內容**：根據玩家行動顯示不同內容
- **分支劇情**：玩家選擇影響故事走向

### 故事結構

```
第1章：故事開端
├── 第2章：找人聊聊
│   ├── 第4章：研究詛咒（結局一）
│   └── 第5章：找到證據（結局二）
└── 第3章：探索王宮
    ├── 第6章：冷靜說服（結局三）
    └── 第7章：武力威脅（結局四）
```

### 新增故事內容

1. **編輯 seed_data.py**：新增章節資料
2. **重新匯入資料**：執行 `python seed_data.py`
3. **測試新章節**：使用 API 或測試腳本驗證

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
story-engine-api/
├── main.py                    # FastAPI 主程式
├── models.py                  # SQLAlchemy 資料模型
├── schemas.py                 # Pydantic 資料結構
├── seed_data.py               # 種子資料匯入腳本
├── test_api.py                # API 測試腳本
├── requirements.txt           # Python 套件需求
├── Procfile                   # Render 部署配置
├── .env.example               # 環境變數範本
├── gpt_tools_definition.json  # GPT 工具定義
├── README.md                  # 專案說明（本檔案）
├── DEPLOYMENT.md              # 部署指南
└── GPT_INTEGRATION.md         # GPT 整合指南
```

## 🔧 技術規格

### 後端技術

- **FastAPI 0.104.1**：現代化的 Python Web 框架
- **SQLAlchemy 2.0.23**：Python SQL 工具包和 ORM
- **PostgreSQL**：關聯式資料庫
- **Pydantic 2.5.0**：資料驗證和設定管理
- **Uvicorn 0.24.0**：ASGI 伺服器

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

- [ ] 新增更多故事內容和分支
- [ ] 實作角色屬性和道具系統
- [ ] 加入戰鬥機制和技能檢定
- [ ] 支援多語言內容

### 中期目標

- [ ] 開發故事編輯器介面
- [ ] 實作玩家進度儲存
- [ ] 新增圖片和音效支援
- [ ] 建立故事分享社群

### 長期目標

- [ ] AI 輔助故事生成
- [ ] 多人協作冒險模式
- [ ] 行動應用程式版本
- [ ] 虛擬實境整合

## 🤝 貢獻指南

歡迎貢獻程式碼、回報問題或提出建議！

### 如何貢獻

1. **Fork 專案**
2. **建立功能分支**：`git checkout -b feature/amazing-feature`
3. **提交變更**：`git commit -m 'Add amazing feature'`
4. **推送分支**：`git push origin feature/amazing-feature`
5. **建立 Pull Request**

### 程式碼規範

- 遵循 PEP 8 Python 編碼規範
- 新增適當的註解和文件
- 撰寫測試案例
- 確保所有測試通過

### 回報問題

請使用 GitHub Issues 回報問題，並提供：

- 詳細的問題描述
- 重現步驟
- 預期行為 vs 實際行為
- 環境資訊（Python 版本、作業系統等）

## 📄 授權條款

本專案採用 MIT 授權條款。詳細內容請參考 [LICENSE](LICENSE) 檔案。

## 🙏 致謝

- **FastAPI**：提供優秀的 Python Web 框架
- **SQLAlchemy**：強大的 Python ORM 工具
- **Render**：便利的雲端部署平台
- **OpenAI**：GPT 技術和 Function Calling 功能

## 📞 聯絡資訊

- **專案維護者**：Manus AI
- **GitHub**：[https://github.com/yourusername/story-engine-api](https://github.com/yourusername/story-engine-api)
- **問題回報**：[GitHub Issues](https://github.com/yourusername/story-engine-api/issues)

---

**開始您的冒險之旅吧！** 🗡️⚔️🛡️
