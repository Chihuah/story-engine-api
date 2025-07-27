#!/usr/bin/env python3
"""
Story Engine API 測試工具
測試多故事支援、條件內容和擲骰功能
支援: 多故事管理 + 數值比較條件 + 完整API測試
"""

import requests
import json
import time
import sys
import os
from typing import Dict, Any, List
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StoryEngineAPITester:
    """Story Engine API 測試類別"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.test_results = []
        
    def log_test_result(self, test_name: str, success: bool, details: str = ""):
        """記錄測試結果"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": time.time()
        }
        self.test_results.append(result)
        
        status = "✅" if success else "❌"
        logger.info(f"{status} {test_name}: {details}")
        
    def test_server_health(self) -> bool:
        """測試伺服器健康狀態"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                self.log_test_result("伺服器健康檢查", True, "服務正常運行")
                return True
            else:
                self.log_test_result("伺服器健康檢查", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test_result("伺服器健康檢查", False, f"連線錯誤: {e}")
            return False
    
    def test_api_documentation(self) -> bool:
        """測試 API 文件端點"""
        try:
            # 測試 OpenAPI JSON
            response = self.session.get(f"{self.base_url}/openapi.json")
            if response.status_code == 200:
                openapi_data = response.json()
                
                # 檢查是否包含優化標記
                has_optimization = False
                for path_data in openapi_data.get("paths", {}).values():
                    for operation in path_data.values():
                        if isinstance(operation, dict) and operation.get("x-openai-isConsequential") is False:
                            has_optimization = True
                            break
                
                details = f"包含 {len(openapi_data.get('paths', {}))} 個端點"
                if has_optimization:
                    details += ", 包含 GPT 優化"
                
                self.log_test_result("OpenAPI 文件", True, details)
                
                # 測試 Swagger UI
                response = self.session.get(f"{self.base_url}/docs")
                if response.status_code == 200:
                    self.log_test_result("Swagger UI", True, "文件頁面可訪問")
                else:
                    self.log_test_result("Swagger UI", False, f"HTTP {response.status_code}")
                
                return True
            else:
                self.log_test_result("OpenAPI 文件", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test_result("API 文件測試", False, f"錯誤: {e}")
            return False
    
    def test_list_stories(self) -> bool:
        """測試列出所有故事"""
        try:
            response = self.session.get(f"{self.base_url}/api/stories")
            if response.status_code == 200:
                data = response.json()
                stories = data.get("stories", [])
                total = data.get("total", 0)
                
                if total > 0:
                    # 檢查故事資料結構
                    first_story = stories[0]
                    required_fields = ["story_id", "title", "description", "author", "table_name"]
                    missing_fields = [field for field in required_fields if field not in first_story]
                    
                    if not missing_fields:
                        details = f"找到 {total} 個故事，資料結構完整"
                        self.log_test_result("列出故事", True, details)
                        return True
                    else:
                        details = f"資料結構不完整，缺少: {missing_fields}"
                        self.log_test_result("列出故事", False, details)
                        return False
                else:
                    self.log_test_result("列出故事", True, "沒有找到故事（可能是空資料庫）")
                    return True
            else:
                self.log_test_result("列出故事", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test_result("列出故事", False, f"錯誤: {e}")
            return False
    
    def test_get_story_info(self) -> bool:
        """測試取得特定故事資訊"""
        try:
            # 先獲取故事列表
            stories_response = self.session.get(f"{self.base_url}/api/stories")
            if stories_response.status_code != 200:
                self.log_test_result("取得故事資訊", False, "無法獲取故事列表")
                return False
            
            data = stories_response.json()
            stories = data.get("stories", [])
            if not stories:
                self.log_test_result("取得故事資訊", True, "沒有可用的故事")
                return True
            
            # 測試第一個故事
            test_story_id = stories[0]["story_id"]
            response = self.session.get(f"{self.base_url}/api/stories/{test_story_id}")
            
            if response.status_code == 200:
                story_info = response.json()
                required_fields = ["story_id", "title", "description", "author", "table_name"]
                missing_fields = [field for field in required_fields if field not in story_info]
                
                if not missing_fields:
                    details = f"故事 {test_story_id} 資訊完整"
                    self.log_test_result("取得故事資訊", True, details)
                    return True
                else:
                    details = f"故事資訊不完整，缺少: {missing_fields}"
                    self.log_test_result("取得故事資訊", False, details)
                    return False
            else:
                self.log_test_result("取得故事資訊", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test_result("取得故事資訊", False, f"錯誤: {e}")
            return False
    
    def test_get_story_chapters(self) -> bool:
        """測試取得故事章節列表"""
        try:
            # 先獲取故事列表
            stories_response = self.session.get(f"{self.base_url}/api/stories")
            if stories_response.status_code != 200:
                self.log_test_result("取得故事章節", False, "無法獲取故事列表")
                return False
            
            data = stories_response.json()
            stories = data.get("stories", [])
            if not stories:
                self.log_test_result("取得故事章節", True, "沒有可用的故事")
                return True
            
            # 測試第一個故事的章節
            test_story_id = stories[0]["story_id"]
            response = self.session.get(f"{self.base_url}/api/stories/{test_story_id}/chapters")
            
            if response.status_code == 200:
                chapters_data = response.json()
                chapters = chapters_data.get("chapters", [])
                total = chapters_data.get("total", 0)
                
                if total > 0:
                    # 檢查章節資料結構
                    first_chapter = chapters[0]
                    required_fields = ["id", "title", "content", "options"]
                    missing_fields = [field for field in required_fields if field not in first_chapter]
                    
                    if not missing_fields:
                        details = f"故事 {test_story_id} 有 {total} 個章節，結構完整"
                        self.log_test_result("取得故事章節", True, details)
                        return True
                    else:
                        details = f"章節結構不完整，缺少: {missing_fields}"
                        self.log_test_result("取得故事章節", False, details)
                        return False
                else:
                    self.log_test_result("取得故事章節", True, f"故事 {test_story_id} 沒有章節")
                    return True
            else:
                self.log_test_result("取得故事章節", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test_result("取得故事章節", False, f"錯誤: {e}")
            return False
    
    def test_story_engine_basic(self) -> bool:
        """測試基本故事引擎功能"""
        try:
            # 先獲取可用的故事列表
            stories_response = self.session.get(f"{self.base_url}/api/stories")
            if stories_response.status_code != 200:
                self.log_test_result("故事引擎基本測試", False, "無法獲取故事列表")
                return False
            
            data = stories_response.json()
            stories = data.get("stories", [])
            if not stories:
                self.log_test_result("故事引擎基本測試", False, "沒有可用的故事")
                return False
            
            # 使用第一個故事進行測試
            test_story_id = stories[0]["story_id"]
            
            # 測試獲取第一章（使用新的 API 端點）
            payload = {
                "game_state": {}
            }
            
            response = self.session.post(
                f"{self.base_url}/api/story_engine/{test_story_id}/1", 
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # 檢查回應結構
                required_fields = ["story_id", "story_title", "chapter_id", "title", "content", "options"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    options_count = len(data.get("options", []))
                    details = f"故事 {test_story_id}，章節 1，{options_count} 個選項"
                    self.log_test_result("故事引擎基本測試", True, details)
                    return True
                else:
                    details = f"回應結構不完整，缺少: {missing_fields}"
                    self.log_test_result("故事引擎基本測試", False, details)
                    return False
            else:
                error_detail = ""
                try:
                    error_data = response.json()
                    error_detail = error_data.get("detail", "")
                except:
                    error_detail = response.text
                
                self.log_test_result("故事引擎基本測試", False, f"HTTP {response.status_code}: {error_detail}")
                return False
                
        except Exception as e:
            self.log_test_result("故事引擎基本測試", False, f"錯誤: {e}")
            return False
    
    def test_conditional_content(self) -> bool:
        """測試條件內容功能"""
        try:
            # 獲取故事列表
            stories_response = self.session.get(f"{self.base_url}/api/stories")
            if stories_response.status_code != 200:
                self.log_test_result("條件內容測試", False, "無法獲取故事列表")
                return False
            
            data = stories_response.json()
            stories = data.get("stories", [])
            if not stories:
                self.log_test_result("條件內容測試", False, "沒有可用的故事")
                return False
            
            test_story_id = stories[0]["story_id"]
            
            # 測試布林條件
            payload_with_state = {
                "game_state": {
                    "has_weapon": True,
                    "health": 75,
                    "strength": 18,
                    "visited_forest": True
                }
            }
            
            response_with_state = self.session.post(
                f"{self.base_url}/api/story_engine/{test_story_id}/1", 
                json=payload_with_state
            )
            
            # 測試無狀態
            payload_no_state = {
                "game_state": {}
            }
            
            response_no_state = self.session.post(
                f"{self.base_url}/api/story_engine/{test_story_id}/1", 
                json=payload_no_state
            )
            
            if response_with_state.status_code == 200 and response_no_state.status_code == 200:
                data_with_state = response_with_state.json()
                data_no_state = response_no_state.json()
                
                content_with_state = data_with_state.get("content", "")
                content_no_state = data_no_state.get("content", "")
                
                # 檢查內容是否不同（表示條件內容生效）
                if content_with_state != content_no_state:
                    self.log_test_result("條件內容測試", True, "條件內容正確處理不同遊戲狀態")
                    return True
                else:
                    # 內容相同可能是正常的，檢查是否有條件內容標記
                    if "[[IF" in content_with_state or "[[IF" in content_no_state:
                        self.log_test_result("條件內容測試", False, "條件內容未正確處理")
                        return False
                    else:
                        self.log_test_result("條件內容測試", True, "該章節無條件內容（正常）")
                        return True
            else:
                self.log_test_result("條件內容測試", False, "API 請求失敗")
                return False
                
        except Exception as e:
            self.log_test_result("條件內容測試", False, f"錯誤: {e}")
            return False
    
    def test_numeric_conditions(self) -> bool:
        """測試數值比較條件"""
        try:
            # 獲取故事列表
            stories_response = self.session.get(f"{self.base_url}/api/stories")
            if stories_response.status_code != 200:
                self.log_test_result("數值條件測試", False, "無法獲取故事列表")
                return False
            
            data = stories_response.json()
            stories = data.get("stories", [])
            if not stories:
                self.log_test_result("數值條件測試", False, "沒有可用的故事")
                return False
            
            test_story_id = stories[0]["story_id"]
            
            # 測試不同的數值條件
            test_cases = [
                {"health": 90, "strength": 20, "description": "高生命值和力量"},
                {"health": 30, "strength": 10, "description": "低生命值和力量"},
                {"health": 50, "strength": 15, "description": "中等數值"}
            ]
            
            results = []
            for test_case in test_cases:
                payload = {
                    "game_state": {k: v for k, v in test_case.items() if k != "description"}
                }
                
                response = self.session.post(
                    f"{self.base_url}/api/story_engine/{test_story_id}/1", 
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results.append({
                        "case": test_case["description"],
                        "content_length": len(data.get("content", "")),
                        "options_count": len(data.get("options", []))
                    })
                else:
                    self.log_test_result("數值條件測試", False, f"請求失敗: {test_case['description']}")
                    return False
            
            # 檢查結果是否有差異（表示數值條件生效）
            if len(set(r["content_length"] for r in results)) > 1 or \
               len(set(r["options_count"] for r in results)) > 1:
                details = f"數值條件正確處理，測試了 {len(test_cases)} 種情況"
                self.log_test_result("數值條件測試", True, details)
                return True
            else:
                self.log_test_result("數值條件測試", True, "該章節無數值條件（正常）")
                return True
                
        except Exception as e:
            self.log_test_result("數值條件測試", False, f"錯誤: {e}")
            return False
    
    def test_dice_rolling(self) -> bool:
        """測試擲骰功能"""
        try:
            # 測試基本擲骰
            basic_payload = {
                "dice_count": 1,
                "dice_sides": 6
            }
            
            response = self.session.post(f"{self.base_url}/api/roll_dice", json=basic_payload)
            
            if response.status_code == 200:
                data = response.json()
                
                # 檢查回應結構
                required_fields = ["dice_count", "dice_sides", "results", "total", "description"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test_result("擲骰基本測試", False, f"回應結構不完整: {missing_fields}")
                    return False
                
                # 檢查結果合理性
                results = data["results"]
                total = data["total"]
                
                if len(results) == 1 and 1 <= results[0] <= 6 and results[0] == total:
                    self.log_test_result("擲骰基本測試", True, f"1d6 = {results[0]}")
                else:
                    self.log_test_result("擲骰基本測試", False, f"結果不合理: {results}, 總和: {total}")
                    return False
            else:
                self.log_test_result("擲骰基本測試", False, f"HTTP {response.status_code}")
                return False
            
            # 測試多顆骰子
            multi_payload = {
                "dice_count": 3,
                "dice_sides": 20
            }
            
            response = self.session.post(f"{self.base_url}/api/roll_dice", json=multi_payload)
            
            if response.status_code == 200:
                data = response.json()
                results = data["results"]
                total = data["total"]
                
                if (len(results) == 3 and 
                    all(1 <= r <= 20 for r in results) and 
                    sum(results) == total):
                    self.log_test_result("多骰子測試", True, f"3d20 = {results} (總和: {total})")
                else:
                    self.log_test_result("多骰子測試", False, f"結果不合理: {results}")
                    return False
            else:
                self.log_test_result("多骰子測試", False, f"HTTP {response.status_code}")
                return False
            
            # 測試修正值
            modifier_payload = {
                "dice_count": 2,
                "dice_sides": 6,
                "modifier": 5
            }
            
            response = self.session.post(f"{self.base_url}/api/roll_dice", json=modifier_payload)
            
            if response.status_code == 200:
                data = response.json()
                results = data["results"]
                total = data["total"]
                modifier = data.get("modifier", 0)
                
                expected_total = sum(results) + modifier
                if total == expected_total:
                    self.log_test_result("修正值測試", True, f"2d6+5 = {results}+{modifier} = {total}")
                else:
                    self.log_test_result("修正值測試", False, f"修正值計算錯誤")
                    return False
            else:
                self.log_test_result("修正值測試", False, f"HTTP {response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            self.log_test_result("擲骰測試", False, f"錯誤: {e}")
            return False
    
    def test_error_handling(self) -> bool:
        """測試錯誤處理"""
        try:
            # 測試無效的故事 ID
            invalid_story_payload = {
                "game_state": {}
            }
            
            response = self.session.post(
                f"{self.base_url}/api/story_engine/nonexistent_story/1", 
                json=invalid_story_payload
            )
            
            if response.status_code == 404:
                self.log_test_result("無效故事ID錯誤處理", True, "正確回傳 404")
            else:
                self.log_test_result("無效故事ID錯誤處理", False, f"預期 404，實際 {response.status_code}")
                return False
            
            # 測試無效的章節 ID
            stories_response = self.session.get(f"{self.base_url}/api/stories")
            if stories_response.status_code == 200:
                data = stories_response.json()
                stories = data.get("stories", [])
                if stories:
                    invalid_chapter_payload = {
                        "game_state": {}
                    }
                    
                    response = self.session.post(
                        f"{self.base_url}/api/story_engine/{stories[0]['story_id']}/99999", 
                        json=invalid_chapter_payload
                    )
                    
                    if response.status_code == 404:
                        self.log_test_result("無效章節ID錯誤處理", True, "正確回傳 404")
                    else:
                        self.log_test_result("無效章節ID錯誤處理", False, f"預期 404，實際 {response.status_code}")
                        return False
            
            # 測試無效的擲骰參數
            invalid_dice_payload = {
                "dice_count": 0,
                "dice_sides": 6
            }
            
            response = self.session.post(f"{self.base_url}/api/roll_dice", json=invalid_dice_payload)
            
            if response.status_code == 422:
                self.log_test_result("無效擲骰參數錯誤處理", True, "正確回傳 422")
            else:
                self.log_test_result("無效擲骰參數錯誤處理", False, f"預期 422，實際 {response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            self.log_test_result("錯誤處理測試", False, f"錯誤: {e}")
            return False
    
    def test_performance(self) -> bool:
        """測試 API 效能"""
        try:
            # 獲取故事列表
            stories_response = self.session.get(f"{self.base_url}/api/stories")
            if stories_response.status_code != 200:
                self.log_test_result("效能測試", False, "無法獲取故事列表")
                return False
            
            data = stories_response.json()
            stories = data.get("stories", [])
            if not stories:
                self.log_test_result("效能測試", False, "沒有可用的故事")
                return False
            
            test_story_id = stories[0]["story_id"]
            
            # 測試多次請求的平均回應時間
            response_times = []
            test_count = 5
            
            for i in range(test_count):
                payload = {
                    "game_state": {"health": 50 + i * 10}
                }
                
                start_time = time.time()
                response = self.session.post(
                    f"{self.base_url}/api/story_engine/{test_story_id}/1", 
                    json=payload
                )
                end_time = time.time()
                
                if response.status_code == 200:
                    response_times.append((end_time - start_time) * 1000)  # 轉換為毫秒
                else:
                    self.log_test_result("效能測試", False, f"請求失敗: {response.status_code}")
                    return False
            
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)
            
            details = f"平均: {avg_response_time:.1f}ms, 最大: {max_response_time:.1f}ms, 最小: {min_response_time:.1f}ms"
            
            if avg_response_time < 1000:  # 1秒內
                self.log_test_result("效能測試", True, details)
                return True
            else:
                self.log_test_result("效能測試", False, f"回應時間過長: {details}")
                return False
                
        except Exception as e:
            self.log_test_result("效能測試", False, f"錯誤: {e}")
            return False
    
    def run_all_tests(self) -> bool:
        """執行所有測試"""
        logger.info("🚀 開始 Story Engine API 測試")
        logger.info(f"🌐 測試目標: {self.base_url}")
        logger.info("=" * 60)
        
        tests = [
            ("伺服器健康檢查", self.test_server_health),
            ("API 文件測試", self.test_api_documentation),
            ("列出故事功能", self.test_list_stories),
            ("取得故事資訊", self.test_get_story_info),
            ("取得故事章節", self.test_get_story_chapters),
            ("故事引擎基本功能", self.test_story_engine_basic),
            ("條件內容處理", self.test_conditional_content),
            ("數值比較條件", self.test_numeric_conditions),
            ("擲骰功能", self.test_dice_rolling),
            ("錯誤處理", self.test_error_handling),
            ("API 效能", self.test_performance)
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            logger.info(f"\n🧪 執行測試: {test_name}")
            try:
                if test_func():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                logger.error(f"❌ 測試異常: {e}")
                failed += 1
            
            # 短暫延遲避免過於頻繁的請求
            time.sleep(0.1)
        
        logger.info("\n" + "=" * 60)
        logger.info("📊 測試結果總結")
        logger.info(f"✅ 通過: {passed}")
        logger.info(f"❌ 失敗: {failed}")
        logger.info(f"📊 總計: {passed + failed}")
        
        if failed == 0:
            logger.info("🎉 所有測試都通過了！API 運作正常。")
            return True
        else:
            logger.error(f"⚠️ 有 {failed} 個測試失敗，請檢查 API 服務。")
            return False
    
    def generate_test_report(self) -> str:
        """生成測試報告"""
        report = {
            "test_summary": {
                "total_tests": len(self.test_results),
                "passed": len([r for r in self.test_results if r["success"]]),
                "failed": len([r for r in self.test_results if not r["success"]]),
                "test_time": time.time()
            },
            "test_results": self.test_results,
            "api_endpoint": self.base_url
        }
        
        return json.dumps(report, indent=2, ensure_ascii=False)

def main():
    """主函數"""
    print("🔧 Story Engine API Tester v1.1")
    print("支援多故事管理和數值比較條件測試")
    print("=" * 50)
    
    # 檢查命令列參數
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:8000"
    
    print(f"🌐 測試目標: {base_url}")
    
    # 檢查服務是否運行
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code != 200:
            print(f"⚠️ 警告: 服務回應狀態碼 {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ 錯誤: 無法連接到服務")
        print(f"   {e}")
        print("\n🔧 請確認:")
        print("1. API 服務是否正在運行")
        print("2. 網址是否正確")
        print("3. 防火牆設定是否允許連線")
        sys.exit(1)
    
    # 執行測試
    tester = StoryEngineAPITester(base_url)
    success = tester.run_all_tests()
    
    # 生成報告
    report_filename = f"api_test_report_{int(time.time())}.json"
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(tester.generate_test_report())
    
    print(f"\n📄 詳細測試報告已儲存至: {report_filename}")
    
    if success:
        print("\n🎯 建議下一步:")
        print("1. 檢查測試報告了解詳細結果")
        print("2. 部署到生產環境")
        print("3. 設定監控和日誌")
        sys.exit(0)
    else:
        print("\n🔧 故障排除建議:")
        print("1. 檢查失敗的測試項目")
        print("2. 查看 API 服務日誌")
        print("3. 確認資料庫連線正常")
        print("4. 檢查環境變數設定")
        sys.exit(1)

if __name__ == "__main__":
    main()

