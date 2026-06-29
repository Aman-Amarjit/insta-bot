import os
import re
import traceback
from database import Database
from content_calendar import ContentCalendar
from content_generator import ContentGenerator
from image_generator import ImageGenerator
from instagram_client import InstagramClient

def main():
    print("🚀 Starting Daily Facts Bot Execution...")
    
    # Track paths to clean up on final completion
    temp_image_path = None
    
    try:
        # 1. Connect to Supabase
        print("🔗 Step 1: Connecting to database...")
        db = Database()
        
        # 2. Get last 100 facts (duplicate prevention)
        print("🔍 Step 2: Retrieving recent facts to prevent duplicates...")
        recent_facts = db.get_recent_facts(limit=100)
        print(f"   Found {len(recent_facts)} recent facts.")
        
        # 3. Determine active category
        print("📅 Step 3: Consulting Content Calendar for category...")
        calendar = ContentCalendar(db=db)
        category = calendar.get_category()
        print(f"   Target category resolved: '{category}'")
        
        # 4. Generate fact via Groq (with JSON-mode & validation)
        print("🤖 Step 4: Generating new fact via Groq API...")
        generator = ContentGenerator()
        fact_data = generator.generate(category=category, recent_facts=recent_facts)
        print(f"   Generated Fact: \"{fact_data.get('fact')}\"")
        
        # 5. Render image via Pillow
        print("🖼️ Step 5: Rendering infographic image via Pillow...")
        image_gen = ImageGenerator()
        temp_image_path = image_gen.render(fact_data)
        print(f"   Infographic rendered successfully at: {temp_image_path}")
        
        # 6. Post to Instagram
        print("📤 Step 6: Posting infographic to Instagram...")
        client = InstagramClient()
        
        # Build the final caption robustly:
        # 1. Strip any hashtags the LLM may have embedded inside the caption body
        # 2. Combine with the dedicated hashtags list and deduplicate
        # 3. Always append a clean, consistent hashtag block at the end
        raw_caption = fact_data.get("caption", "")
        hashtags_list = fact_data.get("hashtags", [])

        # Extract hashtags already embedded in the raw caption (e.g. #facts #science)
        embedded_tags = re.findall(r'#\w+', raw_caption)
        # Strip those embedded hashtags from the caption body to get clean prose
        caption_body = re.sub(r'\s*#\w+', '', raw_caption).strip()

        # Combine embedded tags with dedicated hashtags array, clean and deduplicate
        all_tags_raw = embedded_tags + (hashtags_list or [])
        seen = set()
        formatted_tags = []
        for tag in all_tags_raw:
            if not tag:
                continue
            tag_cleaned = tag.strip().replace(" ", "")
            if not tag_cleaned.startswith("#"):
                tag_cleaned = f"#{tag_cleaned}"
            tag_lower = tag_cleaned.lower()
            if tag_lower not in seen:
                seen.add(tag_lower)
                formatted_tags.append(tag_cleaned)

        # Assemble: clean caption body + blank line + hashtags block
        if formatted_tags:
            hashtags_str = " ".join(formatted_tags)
            final_caption = f"{caption_body}\n\n{hashtags_str}"
        else:
            final_caption = caption_body
        
        print(f"   Caption body length: {len(caption_body)} chars, Tags: {len(formatted_tags)}")

        media = client.post_photo_with_music(image_path=temp_image_path, caption=final_caption, category=category)
        instagram_id = media.id if media else None
        print(f"   Instagram post completed. Media ID: {instagram_id}")
        
        # 7. Save record back to Supabase
        print("💾 Step 7: Saving post record in Supabase...")
        db.save_post(
            fact_text=fact_data.get("fact"),
            caption=final_caption,
            category=category,
            instagram_id=instagram_id
        )
        print("✅ Step 7 completed successfully.")
        
    except Exception as e:
        print("\n❌ CRITICAL EXCEPTION: Execution failed!")
        traceback.print_exc()
        # Re-raise to trigger failure step in GitHub Actions
        raise e
        
    finally:
        # 8. Cleanup temporary image file
        if temp_image_path and os.path.exists(temp_image_path):
            print(f"🧹 Step 8: Cleaning up temporary file: {temp_image_path}...")
            try:
                os.remove(temp_image_path)
                print("   Cleanup finished.")
            except Exception as ce:
                print(f"   ⚠️ Cleanup warning: Could not delete temp file: {ce}")
                
    print("\n🏁 Daily Facts Bot completed execution successfully!")

if __name__ == "__main__":
    main()
