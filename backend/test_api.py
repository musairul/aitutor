# Simple test script to verify the backend is working
import requests
import json

BASE_URL = "http://localhost:5000/api"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL.replace('/api', '')}/api/health")
        print(f"✓ Health check: {response.json()}")
        return True
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False

def test_signup():
    """Test signup"""
    try:
        response = requests.post(f"{BASE_URL}/auth/signup", json={
            "username": "testuser",
            "password": "testpass"
        })
        if response.status_code == 201:
            print(f"✓ Signup successful")
            return response.json()['access_token']
        else:
            print(f"✗ Signup failed: {response.json()}")
            # Try login instead
            return test_login()
    except Exception as e:
        print(f"✗ Signup failed: {e}")
        return None

def test_login():
    """Test login"""
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "username": "testuser",
            "password": "testpass"
        })
        if response.status_code == 200:
            print(f"✓ Login successful")
            return response.json()['access_token']
        else:
            print(f"✗ Login failed: {response.json()}")
            return None
    except Exception as e:
        print(f"✗ Login failed: {e}")
        return None

def test_create_module(token):
    """Test module creation"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{BASE_URL}/modules/", 
            headers=headers,
            data={
                "name": "Test Module",
                "emoji": "📚"
            }
        )
        if response.status_code == 201:
            print(f"✓ Module created: {response.json()}")
            return response.json()['id']
        else:
            print(f"✗ Module creation failed: {response.json()}")
            return None
    except Exception as e:
        print(f"✗ Module creation failed: {e}")
        return None

def test_get_modules(token):
    """Test getting modules"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/modules/", headers=headers)
        if response.status_code == 200:
            modules = response.json()
            print(f"✓ Retrieved {len(modules)} modules")
            return True
        else:
            print(f"✗ Get modules failed: {response.json()}")
            return False
    except Exception as e:
        print(f"✗ Get modules failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Testing AI Tutor Backend")
    print("=" * 50)
    print()
    
    # Test health
    if not test_health():
        print("\n❌ Backend is not running. Please start it with: python app.py")
        exit(1)
    
    print()
    
    # Test authentication
    token = test_signup()
    if not token:
        print("\n❌ Authentication failed")
        exit(1)
    
    print()
    
    # Test module operations
    test_get_modules(token)
    module_id = test_create_module(token)
    if module_id:
        test_get_modules(token)
    
    print()
    print("=" * 50)
    print("✅ All tests completed!")
    print("=" * 50)
