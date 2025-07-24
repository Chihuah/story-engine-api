# GPT 整合指南

本指南說明如何將「GPTs 互動式冒險故事引擎」整合到自訂 GPT 中，讓 GPT 能夠透過 Function Calling 機制載入故事章節和執行擲骰檢定。

## 概述

這個故事引擎提供兩個核心功能：

1. **story_engine**：載入故事章節內容與選項
2. **roll_dice**：執行擲骰子檢定

GPT 將作為遊戲主持人（Game Master），透過這些工具來驅動互動式冒險故事的進行。

## 前置準備

### 1. 部署 API 服務

確保您已經按照 `DEPLOYMENT.md` 的指示完成以下步驟：

- 將 API 部署到 Render 或其他雲端平台
- 設定 PostgreSQL 資料庫
- 匯入故事章節資料
- 驗證 API 正常運作

### 2. 取得 API 端點 URL

記錄您的 API 基礎 URL，格式類似：

```
https://your-app-name.onrender.com
```

## GPT 設定步驟

### 步驟一：建立自訂 GPT

1. 前往 [ChatGPT](https://chat.openai.com)
2. 點擊左側選單中的 **"Explore"**
3. 點擊 **"Create a GPT"**
4. 選擇 **"Configure"** 標籤進行手動設定

### 步驟二：基本資訊設定

填入以下基本資訊：

- **Name**: `互動式冒險故事主持人`
- **Description**: `專業的冒險故事遊戲主持人，能夠載入故事章節、處理玩家選擇，並執行擲骰檢定來驅動劇情發展。`

### 步驟三：設定 Instructions

在 **Instructions** 欄位中輸入以下指示：

```
你是一位專業的互動式冒險故事遊戲主持人。你的任務是：

1. **故事敘述**：使用 story_engine 工具載入故事章節，向玩家生動地描述當前情境
2. **選項呈現**：清楚地向玩家展示所有可選擇的行動選項
3. **擲骰檢定**：當劇情需要隨機判定時，使用 roll_dice 工具執行檢定
4. **狀態管理**：追蹤玩家的遊戲狀態，並在載入章節時傳遞相關狀態

## 遊戲流程

### 開始遊戲
- 使用 story_engine 載入第 1 章開始故事
- 生動地描述場景和情境
- 向玩家展示可選擇的行動

### 處理玩家選擇
- 根據玩家的選擇載入對應的下一章節
- 更新遊戲狀態（如獲得道具、觸發事件等）
- 繼續推進故事

### 擲骰檢定
- 當遇到需要運氣或技能判定的情況時，詢問玩家是否要進行檢定
- 使用適當的骰子類型（如 D6、D20）
- 根據擲骰結果決定劇情走向

### 遊戲狀態
追蹤以下狀態變數：
- found_secret_path: 是否發現密道
- has_key: 是否擁有鑰匙
- 其他劇情相關狀態

## 敘述風格
- 使用第二人稱（「你」）來稱呼玩家
- 營造緊張刺激的氛圍
- 詳細描述場景和角色
- 在關鍵時刻建議進行擲骰檢定

## 範例對話
玩家：「我想開始一個新的冒險故事」
你：「歡迎來到這個充滿魔法與詛咒的世界！讓我為你載入故事的開端...」
[使用 story_engine 載入第 1 章]

記住：你的目標是創造一個引人入勝、互動性強的冒險體驗！
```

### 步驟四：新增 Actions（工具）

1. 在 **Actions** 區段點擊 **"Create new action"**
2. 選擇 **"Import from URL"**
3. 輸入您的 API OpenAPI 文件 URL：
   ```
   https://your-app-name.onrender.com/openapi.json
   ```
4. 點擊 **"Import"**

如果自動匯入失敗，可以手動設定：

#### 手動設定 Actions

1. 點擊 **"Create new action"**
2. 在 **Schema** 欄位中貼上以下 OpenAPI 規格：

```json
{
  "openapi": "3.0.0",
  "info": {
    "title": "GPTs 互動式冒險故事引擎",
    "version": "1.0.0"
  },
  "servers": [
    {
      "url": "https://your-app-name.onrender.com"
    }
  ],
  "paths": {
    "/story_engine": {
      "post": {
        "operationId": "story_engine",
        "summary": "載入故事章節",
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": {
                  "chapter_id": {
                    "type": "integer",
                    "description": "章節 ID"
                  },
                  "game_state": {
                    "type": "object",
                    "description": "遊戲狀態"
                  }
                },
                "required": ["chapter_id"]
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "成功載入章節",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "chapter_id": { "type": "integer" },
                    "title": { "type": "string" },
                    "content": { "type": "string" },
                    "options": {
                      "type": "array",
                      "items": {
                        "type": "object",
                        "properties": {
                          "text": { "type": "string" },
                          "next_id": { "type": "integer" }
                        }
                      }
                    },
                    "game_state": { "type": "object" }
                  }
                }
              }
            }
          }
        }
      }
    },
    "/roll_dice": {
      "post": {
        "operationId": "roll_dice",
        "summary": "擲骰子檢定",
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": {
                  "dice_sides": {
                    "type": "integer",
                    "description": "骰子面數"
                  },
                  "dice_count": {
                    "type": "integer",
                    "description": "骰子數量"
                  }
                },
                "required": ["dice_sides", "dice_count"]
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "擲骰結果",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "rolls": {
                      "type": "array",
                      "items": { "type": "integer" }
                    },
                    "total": { "type": "integer" },
                    "description": { "type": "string" }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
```

**重要**：請將 `https://your-app-name.onrender.com` 替換為您實際的 API URL。

### 步驟五：測試設定

1. 點擊 **"Test"** 按鈕測試 Actions 是否正常工作
2. 嘗試呼叫 `story_engine` 載入第 1 章
3. 嘗試呼叫 `roll_dice` 執行擲骰

### 步驟六：發布 GPT

1. 確認所有設定都正確無誤
2. 點擊 **"Save"** 儲存設定
3. 選擇發布範圍（僅自己使用、連結分享、或公開）

## 使用範例

### 開始新遊戲

**玩家**：「我想開始一個新的冒險故事」

**GPT 回應**：

```
歡迎來到這個充滿魔法與詛咒的神秘世界！讓我為你載入故事的開端...

[呼叫 story_engine(chapter_id=1)]

=== 故事開端 ===

「聽我說，別管什麼詛咒和魔法，還有弗爾泰斯特的妄想，太危險了。在你們破除魔咒以前，不知道還有多少人會犧牲。殺了那頭怪物，我會像告示寫的一樣付錢給你們，我保證。」

殺了吸血妖鳥，還是解除公主身上的詛咒，你們應該聽從誰的才對？面對沉重的兩難，你們商量不出結果，只能捲起袖子辦事，看看能找到什麼方向。

你現在有兩個選擇：

1. 這麼多年來，王宮裡的日子都是在恐懼中渡過的，無論貴族還是僕人，想必都希望早日擺脫這個夢魘。如果好言相勸，他們或許會願意透露更多情報。

2. 七年又七年，王宮的牆垣始終安靜看著這齣悲劇。在長廊與廳堂間走走，或許它們會說出什麼線索。

請告訴我你的選擇，或者如果你想進行任何檢定，我也可以為你擲骰子！
```

### 處理玩家選擇

**玩家**：「我選擇第一個選項，去找人聊聊」

**GPT 回應**：

```
很好的選擇！你決定先從宮中的人們那裡了解情況...

[呼叫 story_engine(chapter_id=2)]

=== 找人聊聊 ===

你們決定先去宮裡的人間清楚前因後果，而你們告訴你的故事，卻聽得你心裡發涼...

[繼續敘述章節內容並提供新的選擇]
```

### 擲骰檢定

**玩家**：「我想嘗試偷偷潛入歐司崔特的房間」

**GPT 回應**：

```
這是一個冒險的行動！讓我們進行一個潛行檢定來看看你是否能成功避開守衛...

[呼叫 roll_dice(dice_sides=20, dice_count=1)]

你擲出了 D20：結果是 15！

憑藉著你敏捷的身手和對王宮布局的了解，你成功地避開了巡邏的守衛，悄悄地接近了歐司崔特的寢宮...

[根據擲骰結果繼續劇情]
```

## 進階功能

### 遊戲狀態管理

GPT 可以追蹤玩家的遊戲狀態，並在載入章節時傳遞：

```
[呼叫 story_engine(chapter_id=2, game_state={"found_secret_path": true})]
```

這會影響章節內容的顯示，例如顯示條件性的文字段落。

### 自訂擲骰規則

根據不同情況使用不同的骰子：

- **簡單檢定**：1D6
- **技能檢定**：1D20
- **傷害判定**：2D6
- **運氣測試**：1D100

### 劇情分支管理

GPT 可以根據玩家的選擇和擲骰結果動態調整劇情走向，創造獨特的遊戲體驗。

## 故障排除

### 常見問題

1. **Actions 無法呼叫**

   - 檢查 API URL 是否正確
   - 確認 API 服務正在運行
   - 驗證 OpenAPI 規格格式

2. **章節載入失敗**

   - 確認章節 ID 存在於資料庫中
   - 檢查資料庫連線狀態
   - 查看 API 錯誤日誌

3. **擲骰功能異常**
   - 確認骰子參數在有效範圍內
   - 檢查 API 回應格式

### 除錯技巧

1. 使用 API 的 `/docs` 端點測試功能
2. 查看 Render 的應用程式日誌
3. 在 GPT 中要求顯示完整的 API 回應

## 擴展建議

### 新增更多故事內容

1. 在資料庫中新增更多章節
2. 設計複雜的分支劇情
3. 加入更多遊戲狀態變數

### 增強遊戲機制

1. 新增角色屬性系統
2. 實作道具和裝備系統
3. 加入戰鬥機制

### 改善使用者體驗

1. 新增故事進度儲存功能
2. 實作多個故事線選擇
3. 加入圖片和音效支援

## 結語

透過這個整合指南，您可以建立一個功能完整的互動式冒險故事 GPT。這個系統提供了靈活的架構，可以輕鬆擴展和自訂，為玩家創造獨特而引人入勝的遊戲體驗。

記住，成功的關鍵在於：

- 清楚的指示設定
- 正確的 API 整合
- 生動的故事敘述
- 適當的擲骰時機

祝您的冒險故事 GPT 能夠為玩家帶來精彩的遊戲體驗！
