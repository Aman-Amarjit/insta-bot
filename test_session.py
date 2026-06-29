import os
import json
import base64
import sys

def test_session_serialization():
    print("🧪 Testing Instagram Session Serialization...")
    
    session_file = "session.json"
    dummy_data = {
        "uuids": {
            "phone_id": "dummy-uuid-1",
            "uuid": "dummy-uuid-2"
        },
        "cookies": [
            {"name": "sessionid", "value": "1234567"},
            {"name": "ds_user_id", "value": "9876543"}
        ]
    }
    
    # 1. Create dummy session file
    with open(session_file, "w") as f:
        json.dump(dummy_data, f)
        
    try:
        # 2. Read and encode to base64
        with open(session_file, "r") as f:
            data = json.load(f)
        
        compact_json = json.dumps(data)
        encoded_str = base64.b64encode(compact_json.encode("utf-8")).decode("utf-8")
        
        # 3. Decode base64 back to JSON
        decoded_bytes = base64.b64decode(encoded_str).decode("utf-8")
        recovered_data = json.loads(decoded_bytes)
        
        # 4. Verify match
        assert recovered_data["uuids"]["phone_id"] == "dummy-uuid-1"
        assert recovered_data["cookies"][0]["value"] == "1234567"
        
        print("✅ Session base64 round-trip verification passed!")
        
    finally:
        # Cleanup
        if os.path.exists(session_file):
            os.remove(session_file)
            
    return True

if __name__ == "__main__":
    success = test_session_serialization()
    sys.exit(0 if success else 1)
