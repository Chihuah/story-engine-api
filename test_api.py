"""
API 測試腳本
測試 story_engine 和 roll_dice API 的基本功能
"""

import requests
import json

# API 基礎 URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """測試健康檢查端點"""
    print("=== 測試健康檢查 ===")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"狀態碼: {response.status_code}")
        print(f"回應: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"錯誤: {e}")
        return False

def test_story_engine():
    """測試故事引擎 API"""
    print("\n=== 測試故事引擎 API ===")
    
    # 測試案例
    test_cases = [
        {
            "name": "載入第1章（故事開端）",
            "data": {"chapter_id": 1}
        },
        {
            "name": "載入第2章並帶入 game_state",
            "data": {
                "chapter_id": 2,
                "game_state": {"found_secret_path": True}
            }
        },
        {
            "name": "載入不存在的章節",
            "data": {"chapter_id": 999}
        }
    ]
    
    for test_case in test_cases:
        print(f"\n--- {test_case['name']} ---")
        try:
            response = requests.post(
                f"{BASE_URL}/story_engine",
                json=test_case["data"]
            )
            print(f"狀態碼: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"章節 ID: {data['chapter_id']}")
                print(f"標題: {data['title']}")
                print(f"內容長度: {len(data['content'])} 字元")
                print(f"選項數量: {len(data['options'])}")
                if data['options']:
                    print("選項:")
                    for i, option in enumerate(data['options'], 1):
                        print(f"  {i}. {option['text'][:50]}... -> 章節 {option['next_id']}")
            else:
                print(f"錯誤回應: {response.text}")
                
        except Exception as e:
            print(f"錯誤: {e}")

def test_roll_dice():
    """測試擲骰子 API"""
    print("\n=== 測試擲骰子 API ===")
    
    # 測試案例
    test_cases = [
        {
            "name": "擲一顆六面骰",
            "data": {"dice_sides": 6, "dice_count": 1}
        },
        {
            "name": "擲兩顆六面骰",
            "data": {"dice_sides": 6, "dice_count": 2}
        },
        {
            "name": "擲一顆二十面骰",
            "data": {"dice_sides": 20, "dice_count": 1}
        },
        {
            "name": "無效的骰子面數",
            "data": {"dice_sides": 1, "dice_count": 1}
        },
        {
            "name": "無效的骰子數量",
            "data": {"dice_sides": 6, "dice_count": 0}
        }
    ]
    
    for test_case in test_cases:
        print(f"\n--- {test_case['name']} ---")
        try:
            response = requests.post(
                f"{BASE_URL}/roll_dice",
                json=test_case["data"]
            )
            print(f"狀態碼: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"擲骰結果: {data['rolls']}")
                print(f"總和: {data['total']}")
                print(f"描述: {data['description']}")
            else:
                print(f"錯誤回應: {response.text}")
                
        except Exception as e:
            print(f"錯誤: {e}")

def main():
    """執行所有測試"""
    print("開始 API 測試...")
    
    # 測試健康檢查
    if not test_health_check():
        print("健康檢查失敗，請確認伺服器是否正在運行")
        return
    
    # 測試故事引擎
    test_story_engine()
    
    # 測試擲骰子
    test_roll_dice()
    
    print("\n=== 測試完成 ===")

if __name__ == "__main__":
    main()

