import os
import json
import base64
from instagrapi import Client
from instagrapi.mixins.challenge import ChallengeChoice
import config

class InstagramClient:
    def __init__(self):
        self.username = config.INSTAGRAM_USERNAME
        self.password = config.INSTAGRAM_PASSWORD
        self.session_base64 = config.INSTAGRAM_SESSION_BASE64
        self.cl = Client()
        self.cl.challenge_code_handler = self.challenge_code_handler
        self.session_file = "session.json"

    def challenge_code_handler(self, username, choice) -> str:
        print(f"\n🔒 Instagram security checkpoint triggered for user: '{username}'")
        print(f"Instagram requires verification via choice: {choice}")
        print("Please check your email or SMS inbox.")
        code = input("Enter the Instagram verification code: ").strip()
        return code

    def login(self) -> bool:
        """
        Attempts to authenticate with Instagram.
        First tries decoding and loading the session from base64 environment settings,
        then tries the local session.json, and finally falls back to username/password.
        """
        # 1. Try decoding session from base64 config (GitHub Secret)
        if self.session_base64:
            print("🔑 Decoding Instagram session from base64 config...")
            try:
                decoded_session = base64.b64decode(self.session_base64).decode("utf-8")
                session_data = json.loads(decoded_session)
                
                # Write to temp file to load via instagrapi
                with open(self.session_file, "w") as f:
                    json.dump(session_data, f)
                
                self.cl.load_settings(self.session_file)
                
                # VERIFY: Resolve account info and verify session is active
                info = self.cl.account_info()
                print(f"✅ Instagram logged in and session verified from base64 config. User ID: {self.cl.user_id}")
                return True
            except Exception as e:
                print(f"⚠️ Base64 session is invalid or expired: {e}. Trying local file...")

        # 2. Try loading local session.json file (if it exists)
        if os.path.exists(self.session_file):
            print("🔑 Loading local session.json settings...")
            try:
                self.cl.load_settings(self.session_file)
                
                # VERIFY: Resolve account info and verify session is active
                info = self.cl.account_info()
                print(f"✅ Instagram logged in and session verified from local session.json. User ID: {self.cl.user_id}")
                return True
            except Exception as e:
                print(f"⚠️ Local session.json is invalid or expired: {e}. Re-authenticating with password...")
                try:
                    os.remove(self.session_file)
                except:
                    pass

        # 3. Fallback to password authentication
        if not self.username or not self.password:
            print("❌ Instagram credentials missing in config. Cannot log in.")
            return False

        print(f"🔑 Re-authenticating password login for user '{self.username}'...")
        try:
            # Login and dump configuration
            self.cl.login(self.username, self.password)
            self.cl.dump_settings(self.session_file)
            print("✅ Successfully logged in via password and dumped session settings.")
            return True
        except Exception as e:
            print(f"❌ Instagram login failed: {e}")
            return False

    def post_photo(self, image_path: str, caption: str):
        """
        Logs in and posts a photo to Instagram (without music).
        Returns the posted media object.
        """
        # Ensure authenticated
        if not self.login():
            raise Exception("Authentication failed. Cannot post to Instagram.")

        print(f"📸 Uploading photo '{image_path}' to Instagram...")
        try:
            # instagrapi handles photo formatting automatically if pillow is installed
            media = self.cl.photo_upload(image_path, caption)
            print(f"🎉 Photo posted successfully! Media ID: {media.id}")
            
            # Save updated session settings in case tokens rotated
            try:
                self.cl.dump_settings(self.session_file)
                print("💾 Saved updated session configuration to session.json")
            except Exception as se:
                print(f"⚠️ Warning: Failed to dump updated session: {se}")
                
            return media
        except Exception as e:
            print(f"❌ Instagram upload failed: {e}")
            raise e

    # Music search queries mapped to each category for relevance
    CATEGORY_MUSIC_QUERIES = {
        "science":    "science discovery ambient",
        "history":    "epic cinematic orchestral",
        "technology": "futuristic electronic ambient",
        "psychology": "calm piano chill",
        "space":      "space ambient cosmic",
        "biology":    "nature chill ambient",
        "geography":  "world travel chill",
    }

    def post_photo_with_music(self, image_path: str, caption: str, category: str = "science"):
        """
        Logs in and posts a photo to Instagram with a trending music track.
        Searches for a track relevant to the post category.
        Falls back gracefully to a regular photo upload if music is unavailable.
        Returns the posted media object.
        """
        if not self.login():
            raise Exception("Authentication failed. Cannot post to Instagram.")

        print(f"📸 Attempting to upload photo with music for category '{category}'...")
        
        # Try to find a music track
        track = None
        query = self.CATEGORY_MUSIC_QUERIES.get(category, "chill ambient music")
        try:
            print(f"🎵 Searching Instagram music for: '{query}'...")
            tracks = self.cl.search_music(query)
            if tracks:
                track = tracks[0]
                print(f"✅ Found track: '{track.title}' by '{track.artist_name}'")
            else:
                print("⚠️ No music tracks found for this query. Falling back to regular upload.")
        except Exception as me:
            print(f"⚠️ Music search failed: {me}. Falling back to regular upload.")

        # Attempt photo upload with music; fall back to regular upload if it fails
        if track:
            try:
                print(f"🎶 Uploading photo with music track: '{track.title}'...")
                media = self.cl.photo_upload_with_music(
                    path=image_path,
                    caption=caption,
                    track=track,
                )
                print(f"🎉 Photo with music posted successfully! Media ID: {media.id}")
                try:
                    self.cl.dump_settings(self.session_file)
                    print("💾 Saved updated session configuration to session.json")
                except Exception as se:
                    print(f"⚠️ Warning: Failed to dump updated session: {se}")
                return media
            except Exception as e:
                print(f"⚠️ Photo upload with music failed: {e}. Falling back to regular upload...")

        # Fallback: regular photo upload without music
        print(f"📸 Uploading photo (without music) to Instagram...")
        try:
            media = self.cl.photo_upload(image_path, caption)
            print(f"🎉 Photo posted successfully (no music)! Media ID: {media.id}")
            try:
                self.cl.dump_settings(self.session_file)
                print("💾 Saved updated session configuration to session.json")
            except Exception as se:
                print(f"⚠️ Warning: Failed to dump updated session: {se}")
            return media
        except Exception as e:
            print(f"❌ Instagram upload failed: {e}")
            raise e
