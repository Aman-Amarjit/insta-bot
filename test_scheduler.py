import sys
from datetime import datetime, timezone, timedelta
from content_calendar import ContentCalendar
from database import Database

class MockDatabase(Database):
    def __init__(self, recent_categories=None):
        self.url = ""
        self.key = ""
        self.client = None
        self.recent_categories = recent_categories if recent_categories else []

    def get_recent_categories(self, limit: int = 10) -> list:
        return self.recent_categories[:limit]

    def get_recent_facts(self, limit: int = 100) -> list:
        return []

def test_category_schedule():
    print("🧪 Testing Category Schedule Rotation...")
    
    db = MockDatabase()
    cal = ContentCalendar(db=db)
    
    # Define custom datetime inputs (Monday is weekday=0)
    # Mon Morning (9:00 AM IST) -> should yield config.CATEGORY_ROTATION[0][0] = "science"
    mon_morning = datetime(2026, 6, 29, 9, 0, tzinfo=timezone(timedelta(hours=5, minutes=30)))
    cat1 = cal.get_default_category(mon_morning)
    print(f"Mon 09:00 IST default category: {cat1}")
    assert cat1 == "science", f"Expected 'science', got '{cat1}'"
    
    # Mon Afternoon (2:00 PM IST -> 14:00) -> should yield config.CATEGORY_ROTATION[0][1] = "history"
    mon_afternoon = datetime(2026, 6, 29, 14, 0, tzinfo=timezone(timedelta(hours=5, minutes=30)))
    cat2 = cal.get_default_category(mon_afternoon)
    print(f"Mon 14:00 IST default category: {cat2}")
    assert cat2 == "history", f"Expected 'history', got '{cat2}'"
    
    # Mon Evening (6:00 PM IST -> 18:00) -> should yield config.CATEGORY_ROTATION[0][2] = "technology"
    mon_evening = datetime(2026, 6, 29, 18, 0, tzinfo=timezone(timedelta(hours=5, minutes=30)))
    cat3 = cal.get_default_category(mon_evening)
    print(f"Mon 18:00 IST default category: {cat3}")
    assert cat3 == "technology", f"Expected 'technology', got '{cat3}'"
    
    print("✅ Schedule rotation checks passed!")
    return True

def test_category_balancing():
    print("🧪 Testing Category Self-Balancing Variety Logic...")
    
    # Scenario: Default is Monday morning -> "science"
    # But recent 10 posts contain 3 or more "science" -> variety balancer should trigger and pick another category
    recent_posts = ["science", "science", "science", "space", "history", "biology", "technology", "psychology", "geography"]
    
    db = MockDatabase(recent_categories=recent_posts)
    cal = ContentCalendar(db=db)
    
    mon_morning = datetime(2026, 6, 29, 9, 0, tzinfo=timezone(timedelta(hours=5, minutes=30)))
    
    # science default count is 3/10 -> balancer should trigger
    resolved_cat = cal.get_category(mon_morning)
    print(f"Balanced category: {resolved_cat}")
    assert resolved_cat != "science", "Expected category to be swapped from science due to overrepresentation"
    
    # The counts in recent_posts:
    # science: 3
    # space: 1
    # history: 1
    # biology: 1
    # technology: 1
    # psychology: 1
    # geography: 1
    # Zero count categories in recent_posts from config.ALL_CATEGORIES:
    # We check: config.ALL_CATEGORIES includes "science", "history", "technology", "psychology", "space", "biology", "geography"
    # Wait, all of them have count >= 1 except if one is missing. All are count=1.
    # The balancer should select one of the count=1 categories that is not science, which it did.
    
    print("✅ Self-balancing checks passed!")
    return True

if __name__ == "__main__":
    s1 = test_category_schedule()
    s2 = test_category_balancing()
    sys.exit(0 if (s1 and s2) else 1)
