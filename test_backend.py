"""
Test the backend API
"""
import requests
import os
import json

API_BASE = "http://localhost:8000"

def test_health():
    """Test if backend is running"""
    print("1. Testing health check...")
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is healthy")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        print("   Start backend with: uvicorn src.backend.main:app --reload")
        return False

def test_upload():
    """Test file upload"""
    print("\n2. Testing upload endpoint...")
    
    # Create a test image if none exists
    test_image = "test_sample.jpg"
    if not os.path.exists(test_image):
        from PIL import Image
        img = Image.new('RGB', (100, 100), color='red')
        img.save(test_image)
        print(f"📁 Created test image: {test_image}")
    
    try:
        with open(test_image, 'rb') as f:
            files = {'file': ('test.jpg', f, 'image/jpeg')}
            response = requests.post(f"{API_BASE}/upload", files=files, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Upload successful")
            print(f"   File ID: {data.get('id')}")
            print(f"   Filename: {data.get('filename')}")
            return True
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Upload test error: {e}")
        return False

def test_cnn_analysis():
    """Test CNN analysis"""
    print("\n3. Testing CNN analysis...")
    
    test_image = "test_sample.jpg"
    if not os.path.exists(test_image):
        print("⚠️  No test image found")
        return False
    
    try:
        with open(test_image, 'rb') as f:
            files = {'file': ('test.jpg', f, 'image/jpeg')}
            response = requests.post(f"{API_BASE}/api/analyze/cnn", files=files, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ CNN analysis successful")
            print(f"   Prediction: {data.get('prediction')}")
            print(f"   Confidence: {data.get('confidence')}%")
            print(f"   Is Fake: {data.get('is_fake')}")
            return True
        else:
            print(f"❌ CNN analysis failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ CNN test error: {e}")
        return False

def test_complete_analysis():
    """Test complete analysis pipeline"""
    print("\n4. Testing complete analysis...")
    
    test_image = "test_sample.jpg"
    if not os.path.exists(test_image):
        print("⚠️  No test image found")
        return False
    
    try:
        with open(test_image, 'rb') as f:
            files = {'file': ('test.jpg', f, 'image/jpeg')}
            response = requests.post(f"{API_BASE}/api/analyze/complete", files=files, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Complete analysis successful!")
            print(f"   Analysis ID: {data.get('id')}")
            
            result = data.get('result', {})
            print(f"   Risk Level: {result.get('risk_level')}")
            print(f"   CNN Confidence: {result.get('cnn_confidence')}%")
            print(f"   ELA Score: {result.get('ela_score')}%")
            print(f"   Metadata Score: {result.get('metadata_score')}%")
            print(f"   Is Fake: {result.get('is_fake')}")
            
            # Check for ELA image
            ela_url = data.get('ela_image_url')
            if ela_url:
                print(f"   ELA Image: {API_BASE}{ela_url}")
            
            return True
        else:
            print(f"❌ Complete analysis failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Complete analysis error: {e}")
        return False

def test_history():
    """Test history endpoint"""
    print("\n5. Testing history endpoint...")
    
    try:
        response = requests.get(f"{API_BASE}/api/history", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ History retrieved")
            print(f"   Count: {data.get('count', 0)} analyses")
            
            history = data.get('history', [])
            if history:
                print(f"\n   Recent analyses:")
                for item in history[:3]:  # Show first 3
                    print(f"   • {item.get('filename')} - {item.get('risk_level')} risk")
            else:
                print("   No analyses yet")
            
            return True
        else:
            print(f"❌ History failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ History test error: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("TRUTHLENS BACKEND TEST")
    print("="*60)
    
    # Check if backend is running
    if not test_health():
        print("\n❌ Backend not running. Cannot continue tests.")
        print("\nTo start backend:")
        print("1. Open terminal in truthlens folder")
        print("2. Run: uvicorn src.backend.main:app --reload")
        print("3. Wait for '🚀 Starting TruthLens Backend...'")
        return False
    
    # Run tests
    tests = [
        test_upload,
        test_cnn_analysis,
        test_complete_analysis,
        test_history
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for result in results if result)
    total = len(results)
    
    print(f"\n✅ Passed: {passed}/{total} tests")
    
    if passed == total:
        print("\n🎉 BACKEND IS WORKING PERFECTLY!")
        print("\nNext steps:")
        print("1. Start dashboard: streamlit run src/frontend/app.py")
        print("2. Open browser: http://localhost:8501")
        print("3. Upload an image and test the full system!")
    else:
        print("\n⚠️  Some tests failed. Fix issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)