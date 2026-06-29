import subprocess
import base64
import json
import os

# ==============================================================================
# Instagram Session Update Utility for GitHub Actions
#
# CRITICAL SECURITY NOTE:
# To run this script successfully in GitHub Actions, the runner needs a GitHub 
# Personal Access Token (GH_PAT) with the following scopes:
#   - Classic PAT: 'repo' scope (which includes secrets read/write)
#   - Fine-grained PAT: Read and Write permissions to repository 'Secrets'
#
# Set GH_PAT as a secret in your repository, and pass it in the workflow step as:
#   env:
#     GH_TOKEN: ${{ secrets.GH_PAT }}
# ==============================================================================

def save_session():
    session_file = "session.json"
    
    if not os.path.exists(session_file):
        print(f"❌ Session file '{session_file}' not found. Cannot save.")
        return False
        
    print("🔄 Reading Instagram session file...")
    try:
        with open(session_file, "r") as f:
            session_data = json.load(f)
            
        # Serialize to compact JSON and encode to base64 string
        compact_json = json.dumps(session_data)
        encoded_session = base64.b64encode(compact_json.encode("utf-8")).decode("utf-8")
        
        print("🔒 Encoding session.json to base64 completed.")
        
        # Check if we are running in an environment that can update secrets
        # (needs GH_TOKEN to be set in environment variables)
        if not os.environ.get("GH_TOKEN"):
            print("⚠️ Warning: GH_TOKEN not found in environment variables.")
            print("Skipping GitHub Secrets update (useful for local dry-runs).")
            return True
            
        print("📤 Updating GitHub Secret 'INSTAGRAM_SESSION' using GitHub CLI...")
        # Run: gh secret set INSTAGRAM_SESSION --body "<encoded_session>"
        process = subprocess.run(
            ["gh", "secret", "set", "INSTAGRAM_SESSION", "--body", encoded_session],
            capture_output=True,
            text=True
        )
        
        if process.returncode == 0:
            print("✅ Successfully updated INSTAGRAM_SESSION secret in GitHub Repository!")
            return True
        else:
            print(f"❌ Failed to set GitHub secret. CLI error: {process.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error while saving session to secrets: {e}")
        return False

if __name__ == "__main__":
    save_session()
