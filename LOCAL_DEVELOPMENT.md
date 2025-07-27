# 本地開發指南

## 互動式冒險故事引擎本地開發環境設定

---

## 📋 概述

本指南將協助您在本地環境中設定和開發互動式冒險故事引擎。我們的系統採用現代化的多表資料庫架構，支援 PostgreSQL 和 SQLite 兩種資料庫選項，讓您可以根據開發需求選擇最適合的配置。

### 開發環境特色

我們的本地開發環境設計考慮了開發者的各種需求和限制。系統支援多種作業系統，包括 Windows、macOS 和 Linux，並且提供了靈活的資料庫選項。對於快速原型開發和測試，您可以使用 SQLite 資料庫，無需安裝額外的資料庫服務。對於更接近生產環境的開發，您可以使用 PostgreSQL 資料庫。

開發環境包含了完整的故事管理工具，讓您可以輕鬆地建立、編輯、驗證和轉換故事內容。我們也提供了詳細的除錯工具和測試腳本，幫助您快速定位和解決問題。

### 系統需求

在開始設定之前，請確保您的系統滿足以下基本需求。您需要 Python 3.8 或更高版本，建議使用 Python 3.11 以獲得最佳效能和相容性。您也需要 Git 來管理程式碼版本，以及一個適合的程式碼編輯器，如 Visual Studio Code、PyCharm 或 Sublime Text。

對於資料庫方面，如果您選擇使用 PostgreSQL，需要安裝 PostgreSQL 12 或更高版本。如果您選擇使用 SQLite，則無需額外安裝，因為 SQLite 已經包含在 Python 標準庫中。

---

## 🚀 快速開始

### 環境準備

首先，確保您的系統已經安裝了 Python 3.8 或更高版本。您可以透過以下命令來檢查 Python 版本：

```bash
python --version
# 或
python3 --version
```

如果您的系統沒有安裝 Python，請前往 [python.org](https://www.python.org/) 下載並安裝最新版本。在 Windows 系統上，建議在安裝時勾選 "Add Python to PATH" 選項。

接下來，建議建立一個虛擬環境來隔離專案依賴。虛擬環境可以避免不同專案之間的套件衝突，是 Python 開發的最佳實踐：

```bash
# 建立虛擬環境
python -m venv story-engine-env

# 啟動虛擬環境
# Windows
story-engine-env\Scripts\activate

# macOS/Linux
source story-engine-env/bin/activate
```

啟動虛擬環境後，您的命令提示字元應該會顯示環境名稱，表示虛擬環境已經啟動。

### 取得專案程式碼

如果您是從 GitHub 取得專案，可以使用以下命令來複製 repository：

```bash
git clone https://github.com/your-username/story-engine-api.git
cd story-engine-api
```

如果您是從壓縮檔案取得專案，請解壓縮到適當的目錄並進入該目錄。

### 安裝依賴套件

進入專案目錄後，首先安裝基本的 Python 依賴套件：

```bash
pip install -r requirements.txt
```

如果您在安裝過程中遇到問題，特別是與 `psycopg2-binary` 相關的編譯錯誤，可以使用以下命令來避免編譯問題：

```bash
pip install --only-binary=:all: psycopg2-binary==2.9.10
```

這個命令會強制使用預編譯的二進位套件，避免在本地編譯時可能遇到的問題。

### 資料庫設定選擇

我們的系統支援兩種資料庫配置：SQLite（適合開發和測試）和 PostgreSQL（適合生產環境模擬）。

**選項一：使用 SQLite（推薦用於開發）**

SQLite 是最簡單的選擇，無需安裝額外的資料庫服務。建立 `.env` 檔案並設定以下內容：

```bash
# 複製環境變數範本
cp .env.example .env

# 編輯 .env 檔案，設定 SQLite 資料庫
echo "DATABASE_URL=sqlite:///./story_engine.db" > .env
```

**選項二：使用 PostgreSQL（推薦用於生產環境模擬）**

如果您想要使用與生產環境相同的 PostgreSQL 資料庫，首先需要安裝 PostgreSQL。

在 Windows 上，您可以從 [postgresql.org](https://www.postgresql.org/download/windows/) 下載安裝程式。在 macOS 上，可以使用 Homebrew：

```bash
brew install postgresql
brew services start postgresql
```

在 Ubuntu/Debian 上：

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

安裝完成後，建立資料庫和使用者：

```bash
# 切換到 postgres 使用者
sudo -u postgres psql

# 在 PostgreSQL 命令列中執行
CREATE DATABASE story_engine;
CREATE USER story_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE story_engine TO story_user;
\q
```

然後在 `.env` 檔案中設定 PostgreSQL 連線：

```
DATABASE_URL=postgresql://story_user:your_password@localhost:5432/story_engine
```

---

## 🔧 開發環境設定

### 初始化資料庫

完成資料庫設定後，需要初始化資料庫結構。我們的系統會自動建立必要的資料表：

```bash
# 測試資料庫連線
python test_db_connection.py

# 初始化資料庫並載入預設故事
python seed_data.py
```

如果您看到成功訊息，表示資料庫已經正確設定並載入了預設的森林冒險故事。

### 啟動開發服務器

現在您可以啟動 FastAPI 開發服務器：

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

`--reload` 參數會讓服務器在程式碼變更時自動重新載入，這對開發非常有用。`--host 0.0.0.0` 讓服務器接受來自任何 IP 的連線，`--port 8000` 指定服務器端口。

服務器啟動後，您可以在瀏覽器中訪問以下 URL：

- API 文件：http://localhost:8000/docs
- ReDoc 文件：http://localhost:8000/redoc
- OpenAPI Schema：http://localhost:8000/openapi.json

### 驗證安裝

為了確保所有功能正常運作，執行我們提供的測試腳本：

```bash
# 執行 API 功能測試
python test_api.py
```

這個腳本會測試所有主要的 API 端點，包括故事列表、章節載入、擲骰功能等。如果所有測試都通過，表示您的開發環境已經正確設定。

---

## 🛠️ 開發工具和工作流程

### 程式碼編輯器設定

**Visual Studio Code 設定**

如果您使用 Visual Studio Code，建議安裝以下擴充套件來提升開發體驗：

- Python：提供 Python 語法高亮和除錯功能
- Pylance：提供進階的 Python 語言支援
- SQLite Viewer：用於查看和編輯 SQLite 資料庫
- REST Client：用於測試 API 端點

您可以在專案根目錄建立 `.vscode/settings.json` 檔案來設定專案特定的設定：

```json
{
  "python.defaultInterpreterPath": "./story-engine-env/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true
  }
}
```

**PyCharm 設定**

如果您使用 PyCharm，建議進行以下設定：

1. 設定 Python 解釋器為虛擬環境中的 Python
2. 啟用程式碼格式化工具（如 Black）
3. 設定資料庫連線以便直接在 IDE 中查看資料
4. 啟用 FastAPI 支援以獲得更好的程式碼提示

### 程式碼品質工具

為了維護程式碼品質，建議使用以下工具：

**程式碼格式化**：

```bash
# 安裝 Black 程式碼格式化工具
pip install black

# 格式化所有 Python 檔案
black .
```

**程式碼檢查**：

```bash
# 安裝 Flake8 程式碼檢查工具
pip install flake8

# 檢查程式碼品質
flake8 .
```

**型別檢查**：

```bash
# 安裝 mypy 型別檢查工具
pip install mypy

# 執行型別檢查
mypy .
```

### Git 工作流程

建議使用以下 Git 工作流程來管理程式碼版本：

**初始設定**：

```bash
# 設定 Git 使用者資訊
git config user.name "Your Name"
git config user.email "your.email@example.com"

# 建立 .gitignore 檔案（如果不存在）
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo ".env" >> .gitignore
echo "story_engine.db" >> .gitignore
```

**日常開發流程**：

```bash
# 建立新的功能分支
git checkout -b feature/new-story-feature

# 進行開發工作
# ... 編輯檔案 ...

# 提交變更
git add .
git commit -m "Add new story feature"

# 推送到遠端 repository
git push origin feature/new-story-feature
```

---

## 📊 資料庫管理

### 多表架構理解

我們的系統採用創新的多表設計，每個故事都有獨立的資料表。這種設計提供了以下優勢：

**資料隔離**：每個故事的資料完全獨立，不會互相影響。這讓故事的備份、還原和維護變得更加簡單。

**效能優化**：當故事數量增加時，查詢效能不會因為單一大表而下降。每個故事表的大小相對較小，查詢速度更快。

**靈活性**：可以為不同的故事設定不同的索引和優化策略。也可以輕鬆地將特定故事遷移到不同的資料庫實例。

### 資料庫結構

**故事註冊表（story_registry）**：
這是系統的核心表，記錄所有已註冊的故事資訊：

```sql
CREATE TABLE story_registry (
    story_id VARCHAR(50) PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    author VARCHAR(255),
    version VARCHAR(50) DEFAULT '1.0',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**故事資料表（動態建立）**：
每個故事都有獨立的資料表，例如 `story_forest_adventure`：

```sql
CREATE TABLE story_forest_adventure (
    id INTEGER PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    options JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 資料庫操作工具

**查看所有故事**：

```bash
# 列出所有已註冊的故事
python seed_data.py --list-stories

# 查看特定故事的章節
python seed_data.py --list-chapters forest_adventure
```

**匯出和匯入**：

```bash
# 匯出特定故事
python seed_data.py --export-story forest_adventure backup.json

# 匯出所有故事
python seed_data.py --export-all all_stories.json

# 匯入故事
python seed_data.py --import-story new_story.json
```

**資料庫維護**：

```bash
# 清除所有故事資料
python seed_data.py --clear-all

# 重建資料庫結構
python seed_data.py --rebuild-db
```

### 直接資料庫存取

如果您需要直接存取資料庫進行除錯或維護，可以使用以下方法：

**SQLite**：

```bash
# 開啟 SQLite 命令列
sqlite3 story_engine.db

# 查看所有表格
.tables

# 查看故事註冊表
SELECT * FROM story_registry;

# 查看特定故事的章節
SELECT * FROM story_forest_adventure;
```

**PostgreSQL**：

```bash
# 連線到 PostgreSQL
psql -h localhost -U story_user -d story_engine

# 查看所有表格
\dt

# 查看故事註冊表
SELECT * FROM story_registry;
```

---

## 🧪 測試和除錯

### 單元測試

我們提供了完整的測試套件來確保系統功能正常。測試分為幾個主要類別：

**API 端點測試**：

```bash
# 執行完整的 API 測試
python test_api.py

# 測試特定功能
python -c "
from test_api import test_story_list
test_story_list()
"
```

**資料庫功能測試**：

```bash
# 測試資料庫連線
python test_db_connection.py

# 測試故事管理功能
python -c "
from seed_data import test_story_operations
test_story_operations()
"
```

**故事驗證測試**：

```bash
# 驗證故事格式
python story_validator.py example_enhanced_story.json

# 測試條件內容解析
python -c "
from main import evaluate_condition
print(evaluate_condition('health > 50', {'health': 75}))
"
```

### 除錯技巧

**啟用詳細日誌**：
在開發過程中，您可以啟用詳細的日誌輸出來追蹤問題：

```python
import logging

# 在 main.py 開頭加入
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

**使用 Python 除錯器**：

```python
# 在需要除錯的地方加入
import pdb; pdb.set_trace()

# 或使用更現代的 breakpoint()
breakpoint()
```

**API 請求除錯**：

```bash
# 使用 curl 測試 API
curl -X GET "http://localhost:8000/api/stories" -H "accept: application/json"

# 測試故事章節載入
curl -X POST "http://localhost:8000/api/story_engine/forest_adventure/1" \
  -H "Content-Type: application/json" \
  -d '{"game_state": {"health": 100}}'
```

**資料庫查詢除錯**：

```python
# 在 models.py 中啟用 SQL 查詢日誌
engine = create_engine(
    DATABASE_URL,
    echo=True  # 這會印出所有 SQL 查詢
)
```

### 效能分析

**API 回應時間測試**：

```bash
# 使用 time 命令測量回應時間
time curl -X GET "http://localhost:8000/api/stories"

# 使用 Apache Bench 進行壓力測試
ab -n 100 -c 10 http://localhost:8000/api/stories
```

**記憶體使用分析**：

```python
# 安裝 memory_profiler
pip install memory_profiler

# 在函數前加入裝飾器
@profile
def your_function():
    pass

# 執行分析
python -m memory_profiler your_script.py
```

---

## 🎨 故事內容開發

### 故事格式規範

我們的故事系統使用 JSON 格式來定義故事內容。每個故事檔案包含完整的章節資訊、選項設定和遊戲狀態管理。

**基本故事結構**：

```json
{
  "story_info": {
    "story_id": "your_story_id",
    "title": "故事標題",
    "description": "故事描述",
    "author": "作者名稱"
  },
  "chapters": [
    {
      "id": 1,
      "title": "章節標題",
      "content": "章節內容...",
      "options": [
        {
          "text": "選項文字",
          "next_chapter": 2,
          "condition": "health > 50",
          "game_state": { "new_variable": true }
        }
      ]
    }
  ]
}
```

### 條件內容系統

我們的條件內容系統支援複雜的邏輯判斷，讓故事能夠根據玩家狀態動態變化。

**布林條件**：

```
[[IF has_sword]]你握著鋒利的劍，準備迎接挑戰。[[ENDIF]]
[[IF NOT has_key]]門是鎖著的，你需要找到鑰匙。[[ENDIF]]
```

**數值比較條件**：

```
[[IF health > 80]]你感覺精力充沛。[[ENDIF]]
[[IF strength >= 18]]你的力量足以推開這扇門。[[ENDIF]]
[[IF gold < 10]]你的錢包幾乎空了。[[ENDIF]]
```

**複合條件**：

```
[[IF has_sword AND strength > 15]]憑藉你的劍術和力量，你有信心面對任何敵人。[[ENDIF]]
[[IF health <= 30 OR poisoned]]你感到身體虛弱，需要休息或治療。[[ENDIF]]
```

### 故事開發工具

**故事驗證器**：

```bash
# 驗證故事格式和邏輯
python story_validator.py your_story.json
```

驗證器會檢查以下項目：

- JSON 格式正確性
- 必要欄位完整性
- 章節引用一致性
- 條件語法正確性
- 遊戲狀態邏輯合理性

**故事轉換器**：

```bash
# 轉換為 Markdown 文件
python story_converter.py your_story.json --markdown story.md

# 生成流程圖
python story_converter.py your_story.json --flowchart story.mmd

# 匯出為 CSV 表格
python story_converter.py your_story.json --csv story.csv

# 顯示統計資訊
python story_converter.py your_story.json --stats
```

**故事編輯輔助**：

```bash
# 建立新故事範本
python seed_data.py --create-template new_story.json

# 複製現有故事作為範本
python seed_data.py --copy-story forest_adventure new_adventure.json
```

### 遊戲平衡設計

在設計故事時，需要考慮遊戲平衡性，確保玩家有合理的挑戰和成就感。

**屬性設計原則**：

- 生命值通常設定在 50-150 之間
- 屬性值（力量、智慧等）通常設定在 1-30 之間
- 金錢和經驗值可以有更大的範圍

**難度曲線設計**：

- 初期章節應該相對簡單，讓玩家熟悉遊戲機制
- 中期逐漸增加挑戰性，引入更複雜的選擇
- 後期提供高難度挑戰，但也要有多種解決方案

**分支設計**：

- 確保每個選擇都有意義和後果
- 避免「假選擇」（看似不同但結果相同的選擇）
- 提供多條路徑達到相同目標

---

## 🔧 自訂和擴展

### 新增自訂 API 端點

如果您需要新增自訂功能，可以在 `main.py` 中新增新的 API 端點：

```python
@app.get("/api/custom/player_stats/{story_id}")
async def get_player_stats(story_id: str, db: Session = Depends(get_db)):
    """取得玩家統計資訊"""
    # 實作您的邏輯
    return {"story_id": story_id, "stats": {}}

@app.post("/api/custom/save_progress")
async def save_progress(request: SaveProgressRequest, db: Session = Depends(get_db)):
    """儲存遊戲進度"""
    # 實作進度儲存邏輯
    return {"success": True}
```

記得同時更新 `schemas.py` 中的資料模型：

```python
class SaveProgressRequest(BaseModel):
    story_id: str
    chapter_id: int
    game_state: Dict[str, Any]
    player_name: Optional[str] = None
```

### 新增自訂條件函數

您可以擴展條件內容系統，新增自訂的條件函數：

```python
def evaluate_custom_condition(condition: str, game_state: dict) -> bool:
    """評估自訂條件"""
    if condition.startswith("CUSTOM:"):
        custom_condition = condition[7:]  # 移除 "CUSTOM:" 前綴

        if custom_condition == "is_weekend":
            from datetime import datetime
            return datetime.now().weekday() >= 5

        elif custom_condition.startswith("random_chance:"):
            import random
            chance = int(custom_condition.split(":")[1])
            return random.randint(1, 100) <= chance

    return False
```

### 新增故事格式支援

如果您想要支援其他故事格式，可以建立新的轉換器：

```python
class TwineConverter:
    """Twine 格式轉換器"""

    def import_from_twine(self, twine_file: str) -> dict:
        """從 Twine 格式匯入故事"""
        # 實作 Twine 格式解析邏輯
        pass

    def export_to_twine(self, story_data: dict) -> str:
        """匯出為 Twine 格式"""
        # 實作 Twine 格式生成邏輯
        pass
```

### 整合外部服務

您可以整合外部服務來增強故事體驗：

**AI 文字生成**：

```python
import openai

async def generate_dynamic_content(prompt: str) -> str:
    """使用 AI 生成動態內容"""
    response = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
```

**圖片生成**：

```python
async def generate_scene_image(description: str) -> str:
    """生成場景圖片"""
    # 整合 DALL-E 或其他圖片生成服務
    pass
```

---

## 🚨 常見問題解決

### 安裝相關問題

**問題：pip 安裝 psycopg2-binary 失敗**

這是最常見的問題之一，通常發生在 Windows 系統上。解決方法：

```bash
# 方法一：使用預編譯版本
pip install --only-binary=:all: psycopg2-binary

# 方法二：如果仍然失敗，改用 SQLite
echo "DATABASE_URL=sqlite:///./story_engine.db" > .env

# 方法三：在 Windows 上安裝 Visual C++ Build Tools
# 下載並安裝 Microsoft C++ Build Tools
```

**問題：Pydantic 版本相容性問題**

如果遇到 Pydantic 相關錯誤，可能是版本相容性問題：

```bash
# 降級到相容版本
pip install pydantic==1.10.13

# 或升級到最新版本
pip install --upgrade pydantic
```

**問題：虛擬環境啟動失敗**

在某些系統上，虛擬環境可能無法正常啟動：

```bash
# Windows PowerShell 執行政策問題
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 或使用 conda 建立環境
conda create -n story-engine python=3.11
conda activate story-engine
```

### 資料庫相關問題

**問題：資料庫連線失敗**

檢查以下項目：

1. 確認 `.env` 檔案中的 DATABASE_URL 設定正確
2. 如果使用 PostgreSQL，確認服務正在運行
3. 檢查資料庫使用者權限
4. 確認防火牆設定

```bash
# 測試資料庫連線
python test_db_connection.py

# 檢查 PostgreSQL 服務狀態
sudo systemctl status postgresql

# 重新啟動 PostgreSQL
sudo systemctl restart postgresql
```

**問題：資料表不存在**

如果遇到資料表不存在的錯誤：

```bash
# 重新建立資料庫結構
python -c "from models import create_tables; create_tables()"

# 或重新執行初始化
python seed_data.py --rebuild-db
```

**問題：資料庫鎖定（SQLite）**

SQLite 資料庫有時會出現鎖定問題：

```bash
# 關閉所有使用資料庫的程序
pkill -f uvicorn

# 刪除鎖定檔案（如果存在）
rm -f story_engine.db-wal story_engine.db-shm

# 重新啟動服務
uvicorn main:app --reload
```

### API 相關問題

**問題：API 回應 500 錯誤**

檢查服務器日誌來診斷問題：

```bash
# 啟用詳細日誌
uvicorn main:app --reload --log-level debug

# 檢查特定錯誤
python -c "
import traceback
try:
    from main import app
    print('App loaded successfully')
except Exception as e:
    traceback.print_exc()
"
```

**問題：CORS 錯誤**

如果在瀏覽器中遇到 CORS 錯誤：

```python
# 在 main.py 中確認 CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 開發環境可以使用 *
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**問題：JSON 序列化錯誤**

如果遇到 JSON 序列化問題：

```python
# 檢查資料類型
import json

try:
    json.dumps(your_data)
except TypeError as e:
    print(f"JSON serialization error: {e}")
    # 檢查是否有不可序列化的物件
```

### 效能相關問題

**問題：API 回應緩慢**

優化建議：

```python
# 新增資料庫索引
from sqlalchemy import Index

# 在模型中新增索引
class Chapter(Base):
    __tablename__ = "story_chapters"

    id = Column(Integer, primary_key=True)
    story_id = Column(String, index=True)  # 新增索引

    __table_args__ = (
        Index('idx_story_chapter', 'story_id', 'id'),
    )
```

```bash
# 使用連線池
pip install sqlalchemy[pool]
```

**問題：記憶體使用過高**

監控和優化記憶體使用：

```python
# 安裝記憶體監控工具
pip install psutil

# 在程式碼中監控記憶體
import psutil
import os

def get_memory_usage():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024  # MB
```

---

## 📈 效能優化

### 資料庫優化

**查詢優化**：

```python
# 使用 select_related 減少查詢次數
from sqlalchemy.orm import selectinload

def get_story_with_chapters(db: Session, story_id: str):
    return db.query(Story).options(
        selectinload(Story.chapters)
    ).filter(Story.story_id == story_id).first()
```

**連線池設定**：

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

**索引策略**：

```sql
-- 為經常查詢的欄位新增索引
CREATE INDEX idx_story_registry_story_id ON story_registry(story_id);
CREATE INDEX idx_chapter_story_id ON story_forest_adventure(id);
```

### 應用程式優化

**快取機制**：

```python
from functools import lru_cache
import time

@lru_cache(maxsize=128)
def get_cached_story_info(story_id: str):
    """快取故事資訊"""
    # 實作快取邏輯
    pass

# 使用 Redis 進行分散式快取
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_story_chapter(story_id: str, chapter_id: int, content: dict):
    key = f"story:{story_id}:chapter:{chapter_id}"
    redis_client.setex(key, 3600, json.dumps(content))  # 快取 1 小時
```

**異步處理**：

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def process_story_async(story_data: dict):
    """異步處理故事資料"""
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        result = await loop.run_in_executor(
            executor,
            process_story_sync,
            story_data
        )
    return result
```

### 前端優化

**API 回應壓縮**：

```python
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

**回應快取**：

```python
from fastapi import Header
from datetime import datetime, timedelta

@app.get("/api/stories")
async def get_stories(
    if_modified_since: str = Header(None)
):
    # 實作條件式請求
    last_modified = get_stories_last_modified()

    if if_modified_since:
        if_modified_since_dt = datetime.fromisoformat(if_modified_since)
        if last_modified <= if_modified_since_dt:
            return Response(status_code=304)  # Not Modified

    stories = get_all_stories()
    response = JSONResponse(stories)
    response.headers["Last-Modified"] = last_modified.isoformat()
    response.headers["Cache-Control"] = "max-age=3600"
    return response
```

---

## 📚 參考資源

### 官方文件

- [FastAPI 官方文件](https://fastapi.tiangolo.com/) - FastAPI 框架的完整文件
- [SQLAlchemy 官方文件](https://docs.sqlalchemy.org/) - SQLAlchemy ORM 的詳細說明
- [Pydantic 官方文件](https://pydantic-docs.helpmanual.io/) - Pydantic 資料驗證庫文件
- [PostgreSQL 官方文件](https://www.postgresql.org/docs/) - PostgreSQL 資料庫文件

### 開發工具

- [Visual Studio Code](https://code.visualstudio.com/) - 推薦的程式碼編輯器
- [PyCharm](https://www.jetbrains.com/pycharm/) - 專業的 Python IDE
- [Postman](https://www.postman.com/) - API 測試工具
- [DBeaver](https://dbeaver.io/) - 通用資料庫管理工具

### Python 套件

- [uvicorn](https://www.uvicorn.org/) - ASGI 服務器
- [pytest](https://pytest.org/) - Python 測試框架
- [black](https://black.readthedocs.io/) - Python 程式碼格式化工具
- [flake8](https://flake8.pycqa.org/) - Python 程式碼檢查工具

### 社群資源

- [FastAPI GitHub](https://github.com/tiangolo/fastapi) - FastAPI 原始碼和問題追蹤
- [Python.org](https://www.python.org/) - Python 官方網站
- [Stack Overflow](https://stackoverflow.com/questions/tagged/fastapi) - FastAPI 相關問題討論
- [Reddit r/Python](https://www.reddit.com/r/Python/) - Python 社群討論

---
