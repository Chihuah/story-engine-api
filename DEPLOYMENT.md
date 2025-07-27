# 部署指南

## 互動式冒險故事引擎 API 部署完整指南

---

## 📋 概述

本指南將協助您將互動式冒險故事引擎 API 部署到生產環境。我們的系統採用現代化的多表資料庫架構，每個故事使用獨立的資料表，提供更好的隔離性和維護性。

### 系統架構特色

我們的故事引擎採用創新的多表設計架構，與傳統的單表方案相比具有顯著優勢。每個故事都擁有獨立的資料表，這種設計不僅提供了更好的資料隔離性，也讓故事管理變得更加靈活。當您需要備份特定故事、進行故事特定的優化，或是處理大量故事資料時，這種架構的優勢就會顯現出來。

系統的核心組件包括 FastAPI 後端框架，它提供了自動生成的 OpenAPI 文件和現代化的異步處理能力。PostgreSQL 資料庫確保了資料的可靠性和擴展性，而我們自訂的 OpenAPI schema 優化則大幅改善了與 ChatGPT 的整合體驗。

### 支援的部署平台

本指南主要針對 Render 平台進行說明，因為它提供了免費的 PostgreSQL 資料庫和簡單的部署流程。不過，我們的系統設計具有良好的可移植性，也可以部署到其他雲端平台如 Heroku、Railway、或 AWS。

---

## 🚀 Render 平台部署（推薦）

Render 是我們推薦的部署平台，因為它提供了免費的 PostgreSQL 資料庫服務，並且部署流程相對簡單。以下是完整的部署步驟。

### 準備工作

在開始部署之前，請確保您已經完成以下準備工作。首先，您需要一個 GitHub 帳號，並且已經將專案程式碼推送到 GitHub repository。如果您還沒有這樣做，請先建立一個新的 repository 並上傳所有專案檔案。

接下來，您需要註冊一個 Render 帳號。前往 [render.com](https://render.com) 並使用您的 GitHub 帳號進行註冊，這樣可以簡化後續的 repository 連接流程。

### 第一步：建立 PostgreSQL 資料庫

登入 Render 控制台後，首先需要建立 PostgreSQL 資料庫。在 Render 儀表板中，點擊 "New +" 按鈕，然後選擇 "PostgreSQL"。

在資料庫設定頁面中，您需要填入以下資訊：

**Name**: 為您的資料庫命名，例如 "story-engine-db"。這個名稱將用於識別您的資料庫實例。

**Database**: 保持預設值 "story_engine" 或自訂資料庫名稱。

**User**: 保持預設值或自訂使用者名稱。

**Region**: 選擇最接近您目標用戶的地區。

**PostgreSQL Version**: 選擇最新的穩定版本，通常是 15 或更高版本。

**Plan**: 對於測試和小規模使用，選擇 "Free" 方案。如果需要更高的效能和儲存空間，可以選擇付費方案。

點擊 "Create Database" 完成建立。資料庫建立完成後，Render 會提供一個 Database URL，格式類似：

```
postgresql://username:password@hostname:port/database_name
```

請妥善保存這個 URL，稍後在設定環境變數時會用到。

### 第二步：建立 Web Service

資料庫建立完成後，接下來建立 Web Service 來部署您的 API 應用程式。在 Render 儀表板中，再次點擊 "New +" 按鈕，這次選擇 "Web Service"。

在 repository 選擇頁面中，選擇 "Connect a repository"，然後從列表中選擇您的 GitHub repository。如果沒有看到您的 repository，可能需要先授權 Render 存取您的 GitHub 帳號。

在服務設定頁面中，填入以下資訊：

**Name**: 為您的服務命名，例如 "story-engine-api"。這個名稱將成為您的服務 URL 的一部分。

**Region**: 選擇與資料庫相同的地區，以減少延遲。

**Branch**: 選擇要部署的分支，通常是 "main" 或 "master"。

**Root Directory**: 如果您的專案在 repository 的根目錄，保持空白。如果在子目錄中，請填入相對路徑。

**Runtime**: 選擇 "Python 3"。

**Build Command**: 填入 `pip install -r requirements.txt`。

**Start Command**: 填入 `uvicorn main:app --host 0.0.0.0 --port $PORT`。

**Plan**: 對於測試使用，選擇 "Free" 方案。

### 第三步：設定環境變數

在服務設定頁面的 "Environment Variables" 區段中，您需要新增以下環境變數：

**DATABASE_URL**: 填入第一步中取得的 PostgreSQL Database URL。

**PYTHONPATH**: 填入 "."，確保 Python 能正確找到模組。

如果您的應用程式需要其他環境變數，也可以在這裡新增。例如，如果您使用了 API 金鑰或其他敏感資訊，都應該透過環境變數來設定。

### 第四步：部署應用程式

完成所有設定後，點擊 "Create Web Service" 開始部署。Render 會自動從您的 GitHub repository 拉取程式碼，安裝依賴套件，並啟動應用程式。

部署過程通常需要幾分鐘時間。您可以在 Render 控制台中查看部署日誌，了解部署進度和任何可能的錯誤訊息。

部署成功後，Render 會提供一個公開的 URL，格式類似：

```
https://your-service-name.onrender.com
```

### 第五步：初始化資料庫

應用程式部署完成後，您需要初始化資料庫結構和載入預設資料。有兩種方式可以完成這個步驟。

**方式一：使用 Render Shell** （推薦，但需要付費）

在 Render 控制台中，找到您的 Web Service，然後點擊 "Shell" 標籤。這會開啟一個終端機介面，讓您可以直接在伺服器上執行命令。

在 Shell 中執行以下命令：

```bash
# 初始化資料庫結構
python -c "from models import create_tables; create_tables()"

# 載入預設故事資料
python seed_data.py
```

**方式二：本地端使用腳本**

於 .env 檔案裡填入 Render PostgreSQL 的 DATABASE_URL

```bash
# 連線至伺服器，載入預設故事資料
python seed_data.py
```

### 第六步：驗證部署

完成所有步驟後，您需要驗證部署是否成功。首先，在瀏覽器中訪問您的 API 文件頁面：

```
https://your-service-name.onrender.com/docs
```

如果看到 Swagger UI 介面，表示 API 服務正常運行。您可以在這個介面中測試各個 API 端點。

接下來，測試故事引擎功能：

```bash
# 測試故事列表
curl https://your-service-name.onrender.com/api/stories

# 測試故事章節載入
curl -X POST "https://your-service-name.onrender.com/api/story_engine/forest_adventure/1" \
  -H "Content-Type: application/json" \
  -d '{"game_state": {}}'

# 測試擲骰功能
curl -X POST "https://your-service-name.onrender.com/api/roll_dice" \
  -H "Content-Type: application/json" \
  -d '{"dice_count": 2, "dice_sides": 6, "modifier": 0}'
```

如果所有測試都返回正確的結果，表示部署成功完成。

---

## 🔧 部署後設定

### SSL 憑證設定

大多數現代雲端平台都會自動提供 SSL 憑證，但如果您需要自訂憑證，可以參考以下步驟：

**Render 平台**：
Render 自動為所有服務提供免費的 SSL 憑證，無需額外設定。

**自訂網域**：
如果您想使用自己的網域，可以在 Render 控制台中新增自訂網域，並按照指示設定 DNS 記錄。

### 效能優化

部署完成後，您可能需要進行一些效能優化：

**資料庫連線池**：
在生產環境中，建議使用連線池來管理資料庫連線：

```python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)
```

**快取設定**：
對於經常存取的故事內容，可以考慮新增快取機制：

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_cached_chapter(story_id: str, chapter_id: int):
    # 快取章節內容
    pass
```

**日誌設定**：
在生產環境中設定適當的日誌等級：

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### 監控和維護

部署完成後，建議設定監控和維護機制：

**健康檢查端點**：
新增健康檢查端點來監控服務狀態：

```python
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}
```

**資料庫備份**：
定期備份資料庫資料，大多數雲端平台都提供自動備份功能。

**更新策略**：
建立更新和部署策略，確保服務的持續可用性。

---

## 🚨 故障排除

### 常見部署問題

**問題 1：資料庫連線失敗**

症狀：應用程式啟動時出現資料庫連線錯誤。

解決方法：

1. 檢查 DATABASE_URL 環境變數是否正確設定
2. 確認資料庫服務是否正常運行
3. 檢查網路連線和防火牆設定
4. 驗證資料庫使用者權限

**問題 2：模組匯入錯誤**

症狀：出現 "ModuleNotFoundError" 或類似的匯入錯誤。

解決方法：

1. 確認 PYTHONPATH 環境變數設定為 "."
2. 檢查 requirements.txt 是否包含所有必要的套件
3. 驗證檔案結構和模組路徑

**問題 3：端口綁定失敗**

症狀：應用程式無法綁定到指定端口。

解決方法：

1. 確認啟動命令使用 `--host 0.0.0.0`
2. 檢查端口設定是否正確
3. 確認沒有其他服務佔用相同端口

**問題 4：靜態檔案載入失敗**

症狀：API 文件頁面無法正常顯示。

解決方法：

1. 檢查 FastAPI 設定是否正確
2. 確認靜態檔案路徑設定
3. 驗證檔案權限設定

### 除錯工具和技巧

**查看應用程式日誌**：

```bash
# Render 平台
# 在控制台中查看 "Logs" 標籤
```

**資料庫連線測試**：

```python
# 建立測試腳本
import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("資料庫連線成功")
except Exception as e:
    print(f"資料庫連線失敗: {e}")
```

**API 端點測試**：

```bash
# 測試基本端點
curl https://your-domain.com/health

# 測試 OpenAPI 文件
curl https://your-domain.com/openapi.json

# 測試故事 API
curl https://your-domain.com/api/stories
```

---

## 📊 效能監控

### 關鍵指標

部署完成後，建議監控以下關鍵指標：

**回應時間**：API 端點的平均回應時間應該保持在合理範圍內，通常小於 500ms。

**錯誤率**：監控 4xx 和 5xx 錯誤的發生率，正常情況下應該保持在很低的水準。

**資料庫效能**：監控資料庫查詢時間和連線數，確保資料庫不會成為效能瓶頸。

**記憶體使用量**：監控應用程式的記憶體使用情況，避免記憶體洩漏。

### 監控工具

**內建監控**：
大多數雲端平台都提供內建的監控工具，可以查看基本的效能指標。

**第三方監控**：
可以考慮使用 New Relic、DataDog 或 Sentry 等第三方監控服務。

**自訂監控**：
也可以實作自訂的監控端點：

```python
import psutil
from datetime import datetime

@app.get("/metrics")
async def get_metrics():
    return {
        "timestamp": datetime.now(),
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').percent
    }
```

---

## 🔐 安全性考量

### 基本安全措施

**環境變數管理**：
所有敏感資訊都應該透過環境變數來管理，絕不要在程式碼中硬編碼密碼或 API 金鑰。

**HTTPS 強制**：
確保所有通訊都透過 HTTPS 進行，大多數雲端平台都會自動提供這個功能。

**輸入驗證**：
我們的 API 使用 Pydantic 進行輸入驗證，確保所有輸入資料都符合預期格式。

**SQL 注入防護**：
使用 SQLAlchemy ORM 可以有效防止 SQL 注入攻擊。

### 進階安全設定

**API 金鑰認證**：
如果需要限制 API 存取，可以新增 API 金鑰認證：

```python
from fastapi import Header, HTTPException

async def verify_api_key(x_api_key: str = Header()):
    if x_api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key
```

**速率限制**：
實作速率限制來防止 API 濫用：

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/api/stories")
@limiter.limit("10/minute")
async def list_stories(request: Request):
    # API 實作
    pass
```

**CORS 設定**：
在生產環境中，建議限制 CORS 允許的來源：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

---

## 📈 擴展性規劃

### 水平擴展

當應用程式需要處理更多流量時，可以考慮水平擴展：

**負載平衡**：
在多個應用程式實例前面設定負載平衡器。

**資料庫讀寫分離**：
設定主從資料庫架構，將讀取操作分散到從資料庫。

**快取層**：
新增 Redis 或 Memcached 快取層來減少資料庫負載。

### 垂直擴展

對於單一實例的效能優化：

**資源升級**：
增加 CPU、記憶體或儲存空間。

**資料庫優化**：
新增索引、優化查詢、調整資料庫設定。

**程式碼優化**：
使用異步處理、連線池、快取等技術。

---

## 📚 參考資源

### 官方文件

- [FastAPI 官方文件](https://fastapi.tiangolo.com/)
- [SQLAlchemy 官方文件](https://docs.sqlalchemy.org/)
- [PostgreSQL 官方文件](https://www.postgresql.org/docs/)
- [Render 官方文件](https://render.com/docs)

### 社群資源

- [FastAPI GitHub Repository](https://github.com/tiangolo/fastapi)
- [PostgreSQL 社群](https://www.postgresql.org/community/)
- [Python 官方網站](https://www.python.org/)

### 相關工具

- [Postman](https://www.postman.com/) - API 測試工具
- [pgAdmin](https://www.pgadmin.org/) - PostgreSQL 管理工具
- [Docker](https://www.docker.com/) - 容器化平台

---
