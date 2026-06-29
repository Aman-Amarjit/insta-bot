import os
from dotenv import load_dotenv

# Load local environment variables for local testing
load_dotenv()

# Watermark Configurations
WATERMARK_TEXT = os.getenv("WATERMARK_TEXT", "@dailyfacts")
try:
    WATERMARK_OPACITY = float(os.getenv("WATERMARK_OPACITY", "0.6"))
except ValueError:
    WATERMARK_OPACITY = 0.6

# Directory configurations
UPLOAD_DIR = "uploads"

# Content Generation Settings
NICHE = "daily facts"
IMAGE_STYLE = "clean minimalist infographic, dark background, bold text"
CAPTION_TONE = "surprising, educational, engaging"
HASHTAG_COUNT = 20

# Post Times configuration
POST_TIMES = ["09:00", "14:00", "19:00"]

# Categories schedule mapping
CATEGORY_ROTATION = {
    0: ["science", "history", "technology"],      # Monday (0: Morning, 1: Afternoon, 2: Evening)
    1: ["technology", "psychology", "space"],     # Tuesday
    2: ["space", "biology", "history"],           # Wednesday
    3: ["history", "science", "psychology"],      # Thursday
    4: ["psychology", "technology", "biology"],   # Friday
    5: ["geography", "space", "science"],         # Saturday
    6: ["science", "history", "geography"]        # Sunday
}

ALL_CATEGORIES = ["science", "history", "technology", "psychology", "space", "biology", "geography"]

# Supabase Configurations
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# Groq Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Instagram Configurations
INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME", "")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD", "")
INSTAGRAM_SESSION_BASE64 = os.getenv("INSTAGRAM_SESSION", "")
