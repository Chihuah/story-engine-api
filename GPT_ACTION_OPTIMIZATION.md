# GPT Action 優化指南

## 減少確認提示，提升對話流暢性

**版本：** 1.0  
**作者：** Manus AI  
**更新日期：** 2024 年 12 月

---

## 📋 問題描述

在使用 ChatGPT 的自訂 GPT 功能時，當 GPT 需要呼叫外部 API 時，系統會要求用戶確認是否允許連線到指定的 API 網址。這種確認機制雖然是為了安全考量，但會打斷對話的連貫性，影響用戶體驗。

### 典型問題場景

- GPT 每次呼叫 API 都要求確認
- 用戶必須手動點擊「確認」才能繼續對話
- 對話流程被頻繁中斷，影響沉浸感

## 🔧 解決方案

### 1. x-openai-isConsequential 標記

OpenAI 提供了 `x-openai-isConsequential` 這個特殊標記，用於控制 API 呼叫的確認行為：

- **設為 `true`**：每次都強制詢問用戶確認
- **設為 `false`**：提供「Always Allow」選項，用戶可以選擇一次性授權
- **未設定**：GET 請求預設為 `false`，其他請求預設為 `true`

### 2. FastAPI 實作方式

我們在 `main.py` 中添加了自訂的 OpenAPI schema 生成函數：

```python
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    from fastapi.openapi.utils import get_openapi
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # 為所有 API 端點添加 x-openai-isConsequential: false
    for path_item in openapi_schema.get("paths", {}).values():
        for operation in path_item.values():
            if isinstance(operation, dict) and "operationId" in operation:
                operation["x-openai-isConsequential"] = False

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

### 3. 效果說明

設定完成後，當 GPT 首次嘗試呼叫 API 時：

- 系統會顯示確認對話框
- 對話框中會出現「Always Allow」按鈕
- 用戶點擊「Always Allow」後，後續的 API 呼叫將不再需要確認

## 🚀 部署步驟

### 步驟 1：更新 FastAPI 程式碼

確保您的 `main.py` 檔案包含上述的自訂 OpenAPI 函數。

### 步驟 2：重新部署服務

```bash
# 如果使用 Render 平台
git add .
git commit -m "Add x-openai-isConsequential optimization"
git push origin main

# 如果本地測試
uvicorn main:app --reload
```

### 步驟 3：驗證 OpenAPI Schema

訪問您的 API 文件頁面，檢查 OpenAPI schema：

```bash
# 查看完整的 OpenAPI schema
curl https://your-api-domain.com/openapi.json
```

確認每個 API 端點都包含 `x-openai-isConsequential: false` 標記。

### 步驟 4：更新 GPT Action

1. 在 ChatGPT 中開啟您的自訂 GPT
2. 進入 Actions 設定頁面
3. 重新匯入或更新 API schema
4. 儲存設定

### 步驟 5：測試優化效果

1. 開始與 GPT 對話
2. 觸發第一次 API 呼叫
3. 在確認對話框中點擊「Always Allow」
4. 後續的 API 呼叫應該不再需要確認

## 📊 優化前後對比

| 項目          | 優化前         | 優化後                             |
| ------------- | -------------- | ---------------------------------- |
| 首次 API 呼叫 | 需要確認       | 需要確認（但有 Always Allow 選項） |
| 後續 API 呼叫 | 每次都需要確認 | 不需要確認                         |
| 對話流暢性    | 頻繁中斷       | 流暢連續                           |
| 用戶體驗      | 較差           | 大幅改善                           |

## ⚠️ 注意事項

### 安全考量

雖然這個優化能夠改善用戶體驗，但也要注意安全性：

1. **API 安全性**：確保您的 API 有適當的安全措施
2. **資料保護**：不要在 API 中處理敏感的個人資料
3. **存取控制**：考慮實作 API 金鑰或其他認證機制

### 限制說明

1. **無法完全關閉**：OpenAI 的安全設計不允許完全關閉確認機制
2. **首次仍需確認**：第一次使用時仍需要用戶確認
3. **瀏覽器相關**：「Always Allow」設定可能與瀏覽器或裝置相關

## 🔍 故障排除

### 問題 1：OpenAPI Schema 未更新

**症狀**：API 文件中沒有看到 `x-openai-isConsequential` 標記

**解決方法**：

```bash
# 清除 FastAPI 的 schema 快取
# 重新啟動服務
uvicorn main:app --reload
```

### 問題 2：GPT 仍然每次都要求確認

**可能原因**：

- GPT Action 中的 schema 未更新
- 用戶未點擊「Always Allow」
- 瀏覽器快取問題

**解決方法**：

1. 重新匯入 API schema 到 GPT Action
2. 清除瀏覽器快取
3. 確保點擊了「Always Allow」按鈕

### 問題 3：API 呼叫失敗

**檢查項目**：

- API 服務是否正常運行
- 網路連線是否正常
- API 網址是否正確

## 📈 效果驗證

### 測試腳本

您可以使用以下腳本驗證 OpenAPI schema 是否正確設定：

```python
import requests
import json

# 取得 OpenAPI schema
response = requests.get("https://your-api-domain.com/openapi.json")
schema = response.json()

# 檢查每個端點是否包含 x-openai-isConsequential
for path, methods in schema.get("paths", {}).items():
    for method, operation in methods.items():
        if isinstance(operation, dict):
            consequential = operation.get("x-openai-isConsequential")
            print(f"{method.upper()} {path}: x-openai-isConsequential = {consequential}")
```

### 預期輸出

```
GET /api/stories: x-openai-isConsequential = False
POST /api/story_engine/{story_id}/{chapter_id}: x-openai-isConsequential = False
POST /api/roll_dice: x-openai-isConsequential = False
GET /api/stories/{story_id}: x-openai-isConsequential = False
...
```

## 🎯 最佳實踐

### 1. API 設計原則

- **冪等性**：確保重複呼叫不會產生副作用
- **無狀態**：每次 API 呼叫都是獨立的
- **錯誤處理**：提供清楚的錯誤訊息

### 2. 用戶體驗優化

- **回應速度**：優化 API 回應時間
- **錯誤恢復**：當 API 呼叫失敗時，提供替代方案
- **進度指示**：對於較長的操作，提供進度回饋

### 3. 安全性考量

- **輸入驗證**：嚴格驗證所有輸入參數
- **輸出過濾**：避免回傳敏感資訊
- **日誌記錄**：記錄重要的 API 呼叫以供審計

## 📚 相關資源

### OpenAI 官方文件

- [GPT Actions 指南](https://platform.openai.com/docs/actions)
- [OpenAPI 規範](https://spec.openapis.org/oas/v3.0.3)

### FastAPI 文件

- [自訂 OpenAPI](https://fastapi.tiangolo.com/advanced/extending-openapi/)
- [中介軟體](https://fastapi.tiangolo.com/tutorial/middleware/)

### 安全性最佳實踐

- [API 安全檢查清單](https://github.com/shieldfy/API-Security-Checklist)
- [OWASP API 安全指南](https://owasp.org/www-project-api-security/)

---

## 📝 總結

透過在 FastAPI 中添加 `x-openai-isConsequential: false` 標記，我們成功地優化了 GPT Action 的用戶體驗。雖然無法完全消除確認提示，但用戶現在可以選擇「Always Allow」來避免重複確認，大幅提升了對話的流暢性。

這個優化對於互動式故事引擎特別重要，因為故事進行過程中需要頻繁呼叫 API 來載入章節內容和處理遊戲狀態，流暢的對話體驗是提供良好遊戲體驗的關鍵。
