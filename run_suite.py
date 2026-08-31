import os
import sys
import subprocess
import webbrowser
import time

def main():
    print("=" * 60)
    print("  🚀 CortexAI Studio - Multi-Tier Engineering Platform")
    print("  White, Key Blue & Warm Cream Modern Design System")
    print("=" * 60)
    print("\nStarting FastAPI backend on http://localhost:8000 ...")

    backend_dir = os.path.join(os.path.dirname(__file__), "backend")
    sys.path.insert(0, backend_dir)

    try:
        import uvicorn
        # Open browser automatically after 1.5 seconds
        def open_browser():
            time.sleep(1.5)
            webbrowser.open("http://localhost:8000")
        
        import threading
        threading.Thread(target=open_browser, daemon=True).start()

        uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True, app_dir=backend_dir)
    except ImportError:
        print("[!] Uvicorn or required dependencies not found.")
        print("[*] Installing dependencies from backend/requirements.txt...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", os.path.join(backend_dir, "requirements.txt")])
        import uvicorn
        uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True, app_dir=backend_dir)

if __name__ == "__main__":
    main()
