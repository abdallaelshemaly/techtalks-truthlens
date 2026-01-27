#!/usr/bin/env python3
"""
TruthLens Dashboard Runner
Entry point for running the Streamlit dashboard.
"""

import os
import sys
import subprocess

def main():
    """Run the TruthLens dashboard."""
    
    print("=" * 60)
    print("🔍 TruthLens - AI-Powered Media Verification Platform")
    print("=" * 60)
    print()
    print("📊 Starting Streamlit Dashboard...")
    print("🌐 Dashboard will be available at: http://localhost:8501")
    print("📝 Press Ctrl+C to stop the server")
    print("-" * 60)
    
    # Get the path to the main app file
    dashboard_path = os.path.join(
        os.path.dirname(__file__),
        "src/frontend/app.py"
    )
    
    # Check if file exists
    if not os.path.exists(dashboard_path):
        print(f"❌ Error: Dashboard file not found at {dashboard_path}")
        print("Please make sure the file structure is correct.")
        return 1
    
    # Start Streamlit
    try:
        result = subprocess.run([
            sys.executable, "-m", "streamlit", "run", dashboard_path
        ])
        return result.returncode
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())