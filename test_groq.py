import sys
import json
from content_generator import ContentGenerator

def test_json_cleaner():
    print("🧪 Testing JSON response cleaning and extraction...")
    gen = ContentGenerator()
    
    # Test case 1: Standard markdown code fence wrapping
    fence_input = "```json\n{\n  \"fact\": \"Test fact 1\",\n  \"category\": \"space\"\n}\n```"
    cleaned1 = gen._clean_json_text(fence_input)
    parsed1 = json.loads(cleaned1)
    assert parsed1["fact"] == "Test fact 1"
    assert parsed1["category"] == "space"
    
    # Test case 2: Conversational preamble/postamble surrounding JSON
    conversation_input = (
        "Sure, here is the fact in JSON format:\n"
        "{\n  \"fact\": \"Test fact 2\",\n  \"category\": \"history\"\n}\n"
        "Hope this helps you out!"
    )
    cleaned2 = gen._clean_json_text(conversation_input)
    parsed2 = json.loads(cleaned2)
    assert parsed2["fact"] == "Test fact 2"
    assert parsed2["category"] == "history"
    
    print("✅ JSON cleaning tests passed!")
    return True

def test_groq_generation():
    print("🧪 Testing Groq Fact Generator...")
    gen = ContentGenerator()
    
    if not gen.client:
        print("ℹ️ content_generator.py is running in Mock Mode (no GROQ_API_KEY env var).")
        print("Testing mock fact retrieval...")
        fact = gen.generate("science", [])
        assert "fact" in fact
        assert "caption" in fact
        print("✅ Mock generation tests passed!")
        return True
        
    try:
        print("Executing live API test for category 'space'...")
        # Run live api check
        fact = gen.generate("space", ["The earth is round"])
        print(f"Fact generated: {fact}")
        assert "fact" in fact
        assert "caption" in fact
        print("✅ Live Groq generation tests passed!")
        return True
    except Exception as e:
        print(f"❌ Live API test failed: {e}")
        return False

if __name__ == "__main__":
    success1 = test_json_cleaner()
    success2 = test_groq_generation()
    sys.exit(0 if (success1 and success2) else 1)
