"""
資料庫連線測試腳本
用於驗證資料庫設定是否正確
"""

import os
from models import SessionLocal, create_tables, Chapter
from dotenv import load_dotenv, find_dotenv

"""顯示環境資訊"""
# 嘗試載入 .env 檔案
dotenv_path = find_dotenv()
if dotenv_path:
    print(f"載入的 .env 檔案路徑: {dotenv_path}")
    load_dotenv(dotenv_path, override=True)
else:
    print("未找到 .env 檔案")

def test_database_connection():
    """測試資料庫連線"""
    print("🔍 測試資料庫連線...")

    try:
        # 測試建立資料表
        print("📋 建立資料表...")
        create_tables()
        print("✅ 資料表建立成功")
        
        # 測試資料庫連線
        print("🔗 測試資料庫連線...")
        db = SessionLocal()
        
        # 測試查詢
        print("📊 測試資料查詢...")
        chapters = db.query(Chapter).all()
        print(f"✅ 找到 {len(chapters)} 個章節")
        
        if len(chapters) == 0:
            print("⚠️  資料庫是空的，請執行 'python seed_data.py' 匯入種子資料")
        else:
            print("📖 章節列表：")
            for chapter in chapters[:3]:  # 只顯示前3個
                print(f"   - 第{chapter.id}章：{chapter.title}")
            if len(chapters) > 3:
                print(f"   ... 還有 {len(chapters) - 3} 個章節")
        
        db.close()
        print("✅ 資料庫連線測試成功！")
        return True
        
    except Exception as e:
        print(f"❌ 資料庫連線測試失敗：{e}")
        print("\n🔧 可能的解決方案：")
        print("1. 檢查 DATABASE_URL 環境變數是否正確設定")
        print("2. 確認 PostgreSQL 服務是否正在運行")
        print("3. 檢查資料庫用戶權限")
        print("4. 嘗試使用 SQLite 進行快速測試：")
        print("   export DATABASE_URL='sqlite:///./story.db'")
        return False

def show_environment_info():
    # 顯示環境變數
    print("🌟 環境資訊：")
    print(f"   DATABASE_URL: {os.environ.get('DATABASE_URL', '未設定')}")
    print(f"   PORT: {os.environ.get('PORT', '未設定')}")
    print(f"   DEBUG: {os.environ.get('DEBUG', '未設定')}")
    print()

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 資料庫連線測試工具")
    print("=" * 50)
    print()
    
    show_environment_info()
    
    if test_database_connection():
        print("\n🎉 所有測試通過！您可以開始使用 API 了。")
        print("\n📝 下一步：")
        print("1. 啟動 API 伺服器：uvicorn main:app --reload")
        print("2. 執行 API 測試：python test_api.py")
        print("3. 查看 API 文件：http://localhost:8000/docs")
    else:
        print("\n🆘 請解決上述問題後重新測試。")
        print("💡 如需協助，請參考 LOCAL_DEVELOPMENT.md 檔案。")

