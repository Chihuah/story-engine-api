# 本地開發環境設定指南

本指南專門針對本地開發環境的常見問題和解決方案。

## 🚨 常見問題與解決方案

### 問題 1：Pydantic 安裝失敗（需要 Rust）

**錯誤訊息：**

```
error: Microsoft Visual C++ 14.0 is required
error: can't find Rust compiler
```

**原因：**
Pydantic 2.x 版本需要 Rust 編譯器來編譯某些組件。

**解決方案：**
我們已將 requirements.txt 中的 Pydantic 版本降級到 1.10.13，這個版本不需要 Rust。

```bash
# requirements.txt 中已更新為：
pydantic==1.10.13  # 而非 pydantic==2.5.0
```

**如果您想使用 Pydantic 2.x：**

1. 安裝 Rust：https://rustup.rs/
2. 或安裝 Visual Studio Build Tools

### 問題 2：psycopg2-binary 編譯失敗

**錯誤訊息：**

```
Error: pg_config executable not found
Error: Microsoft Visual C++ 14.0 is required
```

**原因：**
pip 嘗試從原始碼編譯 psycopg2-binary，但缺少 PostgreSQL 開發標頭檔或編譯工具。

**解決方案：**
使用 `--only-binary` 參數強制安裝預編譯的二進位版本：

```bash
# 不要在 requirements.txt 中包含 psycopg2-binary
# 而是單獨安裝：
pip install --only-binary=:all: psycopg2-binary==2.9.10
```

**替代方案：**
如果上述方法仍然失敗，可以嘗試：

```bash
# 方案 1：使用 conda
conda install psycopg2

# 方案 2：安裝 PostgreSQL 開發套件（Linux）
sudo apt-get install libpq-dev python3-dev

# 方案 3：使用 Docker 開發環境（見下方）
```

## 🐳 Docker 開發環境（推薦）

如果您遇到太多本地環境問題，建議使用 Docker：

### 建立 Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 複製需求檔案
COPY requirements.txt .

# 安裝 Python 依賴
RUN pip install -r requirements.txt
RUN pip install --only-binary=:all: psycopg2-binary==2.9.10

# 複製應用程式碼
COPY . .

# 暴露端口
EXPOSE 8000

# 啟動命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

### 建立 docker-compose.yml

```yaml
version: "3.8"

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/storyengine
    depends_on:
      - db
    volumes:
      - .:/app

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=storyengine
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### 使用 Docker 開發

```bash
# 啟動服務
docker-compose up -d

# 初始化資料庫
docker-compose exec app python seed_data.py

# 查看日誌
docker-compose logs -f app

# 停止服務
docker-compose down
```

## 🔧 本地 PostgreSQL 設定

### Windows

1. 下載並安裝 PostgreSQL：https://www.postgresql.org/download/windows/
2. 建立資料庫：
   ```sql
   CREATE DATABASE storyengine;
   CREATE USER storyuser WITH PASSWORD 'password';
   GRANT ALL PRIVILEGES ON DATABASE storyengine TO storyuser;
   GRANT USAGE ON SCHEMA public TO storyuser;
   GRANT CREATE ON SCHEMA public TO storyuser;
   ```

### macOS

```bash
# 使用 Homebrew 安裝
brew install postgresql
brew services start postgresql

# 建立資料庫
createdb storyengine
```

### Linux (Ubuntu/Debian)

```bash
# 安裝 PostgreSQL
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# 切換到 postgres 用戶
sudo -u postgres psql

# 建立資料庫和用戶
CREATE DATABASE storyengine;
CREATE USER storyuser WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE storyengine TO storyuser;
\q
```

## 🌐 環境變數設定

### .env 檔案範例

```bash
# 複製 .env.example 為 .env
cp .env.example .env
```

編輯 .env 檔案：

```bash
# 本地 PostgreSQL
DATABASE_URL=postgresql://storyuser:password@localhost:5432/storyengine

# 或使用 SQLite 進行快速測試
# DATABASE_URL=sqlite:///./story.db

# 開發模式
DEBUG=True
PORT=8000
```

### SQLite 快速測試

如果您只是想快速測試功能，可以使用 SQLite：

1. 更新 models.py：

   ```python
   # 在 models.py 中修改
   DATABASE_URL = os.environ.get(
       "DATABASE_URL",
       "sqlite:///./story.db"  # 預設使用 SQLite
   )
   ```

2. 不需要安裝 psycopg2-binary
3. 直接執行：
   ```bash
   python seed_data.py
   uvicorn main:app --reload
   ```

## 🧪 測試本地設定

### 1. 測試資料庫連線

```python
# test_db_connection.py
from models import SessionLocal, create_tables

try:
    create_tables()
    db = SessionLocal()
    print("✅ 資料庫連線成功！")
    db.close()
except Exception as e:
    print(f"❌ 資料庫連線失敗：{e}")
```

### 2. 測試 API 啟動

```bash
# 啟動開發伺服器
uvicorn main:app --reload --host 127.0.0.1 --port 8000

# 在另一個終端測試
curl http://localhost:8000/health
```

### 3. 執行完整測試

```bash
python test_api.py
```

## 📝 開發工作流程

### 推薦的開發步驟

1. **環境準備**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或 venv\Scripts\activate  # Windows
   ```

2. **安裝依賴**

   ```bash
   pip install -r requirements.txt
   pip install --only-binary=:all: psycopg2-binary==2.9.10
   ```

3. **設定環境變數**

   ```bash
   cp .env.example .env
   # 編輯 .env 檔案
   ```

4. **初始化資料庫**

   ```bash
   python seed_data.py
   ```

5. **啟動開發伺服器**

   ```bash
   uvicorn main:app --reload
   ```

6. **測試功能**
   ```bash
   python test_api.py
   ```

## 🔍 除錯技巧

### 查看詳細錯誤

```bash
# 啟動時顯示詳細日誌
uvicorn main:app --reload --log-level debug
```

### 檢查套件版本

```bash
pip list | grep -E "(fastapi|pydantic|sqlalchemy|psycopg2)"
```

### 測試資料庫查詢

```python
# debug_db.py
from models import SessionLocal, Chapter
from sqlalchemy import text

db = SessionLocal()

# 測試基本查詢
chapters = db.query(Chapter).all()
print(f"找到 {len(chapters)} 個章節")

# 測試原始 SQL
result = db.execute(text("SELECT version()")).fetchone()
print(f"資料庫版本：{result[0] if result else '無法取得'}")

db.close()
```

## 🆘 尋求協助

如果您仍然遇到問題：

1. **檢查錯誤日誌**：記錄完整的錯誤訊息
2. **確認環境**：Python 版本、作業系統、已安裝的套件
3. **嘗試 Docker**：使用 Docker 環境可以避免大部分本地環境問題
4. **查看文件**：FastAPI、SQLAlchemy、PostgreSQL 官方文件
5. **社群支援**：Stack Overflow、GitHub Issues

## 📚 相關資源

- [FastAPI 官方文件](https://fastapi.tiangolo.com/)
- [SQLAlchemy 官方文件](https://docs.sqlalchemy.org/)
- [PostgreSQL 官方文件](https://www.postgresql.org/docs/)
- [Pydantic 官方文件](https://pydantic-docs.helpmanual.io/)
- [Docker 官方文件](https://docs.docker.com/)

---
