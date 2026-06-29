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
                
                # VERIFY: Resolve user ID and verify session is active
                user_id = self.cl.user_id_from_username(self.username)
                self.cl.user_id = user_id
                print(f"✅ Instagram logged in and session verified from base64 config. User ID: {user_id}")
                return True
            except Exception as e:
                print(f"⚠️ Base64 session is invalid or expired: {e}. Trying local file...")

        # 2. Try loading local session.json file (if it exists)
        if os.path.exists(self.session_file):
            print("🔑 Loading local session.json settings...")
            try:
                self.cl.load_settings(self.session_file)
                
                # VERIFY: Resolve user ID and verify session is active
                user_id = self.cl.user_id_from_username(self.username)
                self.cl.user_id = user_id
                print(f"✅ Instagram logged in and session verified from local session.json. User ID: {user_id}")
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
        Logs in and posts a photo to Instagram.
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
