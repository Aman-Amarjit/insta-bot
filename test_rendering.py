import os
import sys
from image_generator import ImageGenerator

def test_image_rendering():
    print("🧪 Testing Image Infographic Renderer...")
    
    image_gen = ImageGenerator()
    
    # 1. Test normal-sized fact rendering
    normal_fact = {
        "fact": "Honey never expires; archaeologists found 3000-year-old honey edible in Egypt.",
        "category": "science"
    }
    
    print("Rendering normal fact infographic...")
    path1 = image_gen.render(normal_fact)
    print(f"Normal fact rendered at: {path1}")
    assert os.path.exists(path1), "Rendered image path must exist"
    
    # 2. Test dynamic scaling with exceptionally long text
    long_fact = {
        "fact": (
            "This is an exceptionally long fact that contains multiple sentences to intentionally "
            "test the dynamic font scaling feature inside the Pillow rendering engine. It should "
            "trigger the system to shrink the font from 48px to 40px, then to 32px, and potentially "
            "down to 24px, and if it still doesn't fit in the layout boundaries it will truncate the text."
        ),
        "category": "technology"
    }
    
    print("Rendering exceptionally long fact infographic (testing font scaling)...")
    path2 = image_gen.render(long_fact)
    print(f"Long fact rendered at: {path2}")
    assert os.path.exists(path2), "Rendered image path must exist"
    
    # Cleanup generated test files
    for p in [path1, path2]:
        if os.path.exists(p):
            os.remove(p)
            
    print("✅ Image rendering tests passed!")
    return True

if __name__ == "__main__":
    try:
        success = test_image_rendering()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        sys.exit(1)
