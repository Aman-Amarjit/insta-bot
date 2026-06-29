import sys
from instagram_client import InstagramClient

def test_login():
    print("🧪 Testing Instagram Login...")
    client = InstagramClient()
    success = client.login()
    if success:
        print("✅ Instagram login test passed!")
        return True
    else:
        print("❌ Instagram login test failed!")
        return False

if __name__ == "__main__":
    success = test_login()
    sys.exit(0 if success else 1)
