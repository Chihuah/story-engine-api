# 部署指南

本指南說明如何將 GPTs 互動式冒險故事引擎部署到 Render 雲端平台。

## 前置準備

1. **GitHub 帳號**：用於儲存程式碼
2. **Render 帳號**：用於部署應用程式
3. **本專案程式碼**：確保所有檔案都已準備完成

## 步驟一：準備 GitHub 儲存庫

### 1.1 建立 GitHub 儲存庫

```bash
# 在專案目錄中初始化 Git
git init

# 新增所有檔案
git add .

# 提交變更
git commit -m "Initial commit: GPTs Interactive Story Engine"

# 連接到 GitHub 儲存庫（請替換為您的儲存庫 URL）
git remote add origin https://github.com/yourusername/story-engine-api.git

# 推送到 GitHub
git push -u origin main
```

### 1.2 確認檔案結構

確保您的儲存庫包含以下檔案：

```
story-engine-api/
├── main.py              # FastAPI 主程式
├── models.py            # SQLAlchemy 資料模型
├── schemas.py           # Pydantic 資料結構
├── seed_data.py         # 種子資料匯入腳本
├── test_api.py          # API 測試腳本
├── requirements.txt     # Python 套件需求
├── Procfile            # Render 部署配置
├── .env.example        # 環境變數範本
├── DEPLOYMENT.md       # 部署指南（本檔案）
└── README.md           # 專案說明
```

## 步驟二：在 Render 建立 Web Service

### 2.1 登入 Render

1. 前往 [Render Dashboard](https://dashboard.render.com)
2. 使用 GitHub 帳號登入

### 2.2 建立新的 Web Service

1. 點擊 **"New +"** 按鈕
2. 選擇 **"Web Service"**
3. 連接您的 GitHub 儲存庫
4. 選擇 `story-engine-api` 儲存庫

### 2.3 配置 Web Service

填入以下設定：

- **Name**: `story-engine-api`（或您偏好的名稱）
- **Environment**: `Python 3`
- **Region**: 選擇最近的區域
- **Branch**: `main`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

## 步驟三：新增 PostgreSQL 資料庫

### 3.1 建立 PostgreSQL 服務

1. 在 Render Dashboard 中，點擊 **"New +"**
2. 選擇 **"PostgreSQL"**
3. 填入資料庫設定：
   - **Name**: `story-engine-db`
   - **Database**: `storyengine`
   - **User**: `storyuser`
   - **Region**: 與 Web Service 相同區域

### 3.2 取得資料庫連線資訊

1. 資料庫建立完成後，進入資料庫詳細頁面
2. 複製 **"External Database URL"**
3. 格式類似：`postgresql://username:password@hostname:5432/database_name`

## 步驟四：設定環境變數

### 4.1 在 Web Service 中設定環境變數

1. 進入您的 Web Service 設定頁面
2. 找到 **"Environment Variables"** 區段
3. 新增以下環境變數：

```
DATABASE_URL = postgresql://username:password@hostname:5432/database_name
```

（使用步驟三取得的實際資料庫 URL）

## 步驟五：部署和初始化

### 5.1 觸發部署

1. 儲存環境變數設定
2. Render 會自動開始部署程序
3. 等待部署完成（通常需要 3-5 分鐘）

### 5.2 初始化資料庫

部署完成後，需要匯入種子資料：

```bash
# 方法一：使用 Render Shell（推薦，但需要付費）
# 在 Web Service 頁面中，點擊 "Shell" 標籤
# 執行以下命令：
python seed_data.py

# 方法二：本地執行（需要設定 DATABASE_URL）
export DATABASE_URL="postgresql://username:password@hostname:5432/database_name"
python seed_data.py
```

## 步驟六：驗證部署

### 6.1 檢查 API 狀態

1. 取得您的 Render 應用程式 URL（格式：`https://your-app-name.onrender.com`）
2. 在瀏覽器中訪問：
   - `https://your-app-name.onrender.com/` - 根路徑
   - `https://your-app-name.onrender.com/health` - 健康檢查
   - `https://your-app-name.onrender.com/docs` - API 文件

### 6.2 測試 API 功能

使用提供的測試腳本：

```bash
# 修改 test_api.py 中的 BASE_URL
BASE_URL = "https://your-app-name.onrender.com"

# 執行測試
python test_api.py
```

## 故障排除

### 常見問題

1. **部署失敗**

   - 檢查 `requirements.txt` 是否正確
   - 確認 `Procfile` 格式正確
   - 查看 Render 的部署日誌

2. **資料庫連線失敗**

   - 確認 `DATABASE_URL` 環境變數設定正確
   - 檢查資料庫服務是否正常運行
   - 確認資料庫 URL 格式（使用 `postgresql://` 而非 `postgres://`）

3. **API 回應錯誤**
   - 檢查種子資料是否已正確匯入
   - 查看應用程式日誌
   - 使用 `/docs` 端點測試 API

### 查看日誌

在 Render Web Service 頁面中：

1. 點擊 **"Logs"** 標籤
2. 查看即時日誌輸出
3. 尋找錯誤訊息和異常

## 更新部署

當您更新程式碼時：

1. 提交變更到 GitHub：

   ```bash
   git add .
   git commit -m "Update: description of changes"
   git push origin main
   ```

2. Render 會自動偵測變更並重新部署

## 安全性注意事項

1. **環境變數**：絕不要將敏感資訊（如資料庫密碼）提交到 Git
2. **CORS 設定**：生產環境中考慮限制 CORS 來源
3. **API 限制**：考慮新增 API 速率限制
4. **資料庫備份**：定期備份 PostgreSQL 資料

## 成本考量

- **Render Free Tier**：

  - Web Service：每月 750 小時免費
  - PostgreSQL：每月 90 天免費，之後 $7/月
  - 應用程式閒置 15 分鐘後會進入睡眠狀態

- **付費方案**：
  - 提供更好的效能和可用性
  - 無睡眠限制
  - 更多資源配額

## 下一步

部署完成後，您可以：

1. 將 API URL 整合到 GPT 中
2. 建立更多故事章節
3. 新增更多功能（如玩家狀態儲存）
4. 優化效能和安全性
