"""  
TruthLens Dashboard Runner
"""

import os
import sys
import subprocess
import time
import threading

def check_browser_opened():
    """Check if browser was already opened by Streamlit."""
    # Streamlit usually opens browser within 2-3 seconds
    time.sleep(4)
    
    # Check if we need to open browser manually
    # Streamlit might fail to open browser on some systems
    print("\n📋 Dashboard Status:")
    print("   If browser didn't open automatically:")
    print("   1. Open your browser manually")
    print("   2. Go to: http://localhost:8501")
    print("\n✅ Dashboard is running successfully!")

def main():
    """Run the TruthLens dashboard."""
    
    print("=" * 60)
    print("🔍 TruthLens - AI-Powered Media Verification Platform")
    print("=" * 60)
    print()
    
    # Define paths
    app_path = "src/frontend/app.py"
    
    if not os.path.exists(app_path):
        print(f"❌ Error: Cannot find {app_path}")
        print(f"Current directory: {os.getcwd()}")
        print("\nExpected structure:")
        print("techtalks-truthlens/")
        print("├── run.py")
        print("└── src/frontend/app.py")
        return 1
    
    print(f"✅ Found app at: {app_path}")
    print("📊 Starting Streamlit Dashboard...")
    print("🌐 URL: http://localhost:8501")
    print("📝 Press Ctrl+C to stop the server")
    print("-" * 60)
    
    # Change to frontend directory
    original_dir = os.getcwd()
    os.chdir("src/frontend")
    
    try:
        # Start a thread to check if browser needs manual opening
        checker_thread = threading.Thread(target=check_browser_opened, daemon=True)
        checker_thread.start()
        
        # Run Streamlit - let it handle browser opening
        # Use --server.headless true to prevent Streamlit from opening browser
        # But then we need to open it manually if it fails
        result = subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--browser.serverAddress", "localhost",
            "--server.headless", "false",  # Let Streamlit try to open browser
            "--browser.gatherUsageStats", "false"
        ])
        return result.returncode
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    finally:
        os.chdir(original_dir)

if __name__ == "__main__":
    sys.exit(main())