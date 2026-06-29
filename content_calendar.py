from datetime import datetime, timedelta, timezone
import config
from database import Database

class ContentCalendar:
    def __init__(self, db: Database = None):
        self.db = db if db else Database()

    def get_ist_now(self) -> datetime:
        """
        Returns the current time in Indian Standard Time (IST).
        """
        utc_now = datetime.now(timezone.utc)
        ist_tz = timezone(timedelta(hours=5, minutes=30))
        return utc_now.astimezone(ist_tz)

    def get_default_category(self, ist_time: datetime = None) -> str:
        """
        Retrieves the default category based on the weekday and time slot.
        """
        if not ist_time:
            ist_time = self.get_ist_now()

        weekday = ist_time.weekday()  # 0: Monday, ..., 6: Sunday
        hour = ist_time.hour

        # Morning slot: before 13:00 (1 PM) IST
        # Evening slot: after 13:00 IST
        slot = 0 if hour < 13 else 1

        # Retrieve default categories list for the day
        day_categories = config.CATEGORY_ROTATION.get(weekday, ["science", "history"])
        
        # Safe array index check
        if slot >= len(day_categories):
            return day_categories[0]
        return day_categories[slot]

    def get_category(self, ist_time: datetime = None) -> str:
        """
        Retrieves the category for the post, balancing it if the default category
        is over-represented in the recent history.
        """
        if not ist_time:
            ist_time = self.get_ist_now()

        default_cat = self.get_default_category(ist_time)
        print(f"Calendar: Default category for {ist_time.strftime('%A %H:%M IST')} is '{default_cat}'.")

        # Fetch recent categories
        recent_cats = self.db.get_recent_categories(limit=10)
        if not recent_cats:
            return default_cat

        # Calculate frequency of the default category
        default_count = recent_cats.count(default_cat)
        
        # Variety check: if this category is >= 30% of the last 10 posts, it's overrepresented
        if default_count >= 3:
            print(f"Calendar variety alert: '{default_cat}' has appeared {default_count} times in last 10 posts.")
            
            # Find the least represented category
            cat_counts = {cat: recent_cats.count(cat) for cat in config.ALL_CATEGORIES}
            
            # Sort categories by count (ascending), filtering out the default if possible
            sorted_cats = sorted(config.ALL_CATEGORIES, key=lambda c: cat_counts.get(c, 0))
            
            # Select the least used category
            fallback_cat = sorted_cats[0]
            if fallback_cat != default_cat:
                print(f"Calendar: Balancing category. Swapping default '{default_cat}' -> '{fallback_cat}' (appeared {cat_counts.get(fallback_cat, 0)} times).")
                return fallback_cat
                
        return default_cat
