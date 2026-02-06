"""
Script to run the backend with proper setup
"""
import os
import subprocess
import sys

def setup_directories():
    """Create necessary directories"""
    directories = [
        "uploads",
        "uploads/ela_samples",
        "reports",
        "logs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"📁 Created: {directory}")
    
    print("✅ All directories created")

def check_dependencies():
    """Check if required packages are installed"""
    required = [
        "fastapi",
        "uvicorn",
        "PIL",
        "sqlite3",
        "torch",
        "torchvision"
    ]
    
    print("🔍 Checking dependencies...")
    
    for package in required:
        try:
            if package == "PIL":
                __import__("PIL")
            elif package == "sqlite3":
                __import__("sqlite3")
            else:
                __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} not installed")
    
    print("\n📦 Install missing packages with:")
    print("pip install -r requirements.txt")

def run_backend():
    """Start the FastAPI server"""
    print("\n🚀 Starting TruthLens Backend...")
    print("🌐 Server will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("\n📝 Press Ctrl+C to stop the server")
    print("-" * 60)
    
    try:
        # Change to src/backend directory
        original_dir = os.getcwd()
        backend_dir = os.path.join(original_dir, "src/backend")
        
        if os.path.exists(backend_dir):
            os.chdir(backend_dir)
        
        # Run uvicorn
        subprocess.run([
            sys.executable, "-m", "uvicorn", "main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ])
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Return to original directory
        os.chdir(original_dir)

def main():
    """Main setup and run function"""
    print("=" * 60)
    print("TRUTHLENS BACKEND SETUP")
    print("=" * 60)
    
    # Setup
    setup_directories()
    check_dependencies()
    
    # Ask to continue
    input("\nPress Enter to start the backend server...")
    
    # Run backend
    run_backend()

if __name__ == "__main__":
    main()