import os
import requests
from datetime import datetime

def notify_failure():
    print("⚠️ Failure Handler triggered.")
    
    # Read environment context
    repo = os.environ.get("GITHUB_REPOSITORY", "unknown-repo")
    run_id = os.environ.get("GITHUB_RUN_ID", "")
    run_url = f"https://github.com/{repo}/actions/runs/{run_id}" if run_id else "N/A"
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    # Webhook triggers
    discord_webhook = os.environ.get("DISCORD_WEBHOOK_URL", "")
    slack_webhook = os.environ.get("SLACK_WEBHOOK_URL", "")
    
    message_content = (
        f"🚨 **Daily Facts Bot Failure Alert** 🚨\n\n"
        f"- **Repository:** `{repo}`\n"
        f"- **Time:** `{timestamp}`\n"
        f"- **Workflow Run:** {run_url}\n\n"
        f"Please check the GitHub Actions logs for details."
    )

    if discord_webhook:
        print("📤 Sending alert to Discord Webhook...")
        payload = {
            "content": message_content,
            "embeds": [{
                "title": "Daily Facts Bot failed",
                "color": 15158332,  # Red color
                "description": f"Workflow execution encountered an error. Check logs at: {run_url}",
                "timestamp": datetime.utcnow().isoformat()
            }]
        }
        try:
            r = requests.post(discord_webhook, json=payload)
            if r.status_code in [200, 204]:
                print("✅ Alert sent to Discord successfully.")
            else:
                print(f"⚠️ Discord Webhook returned code: {r.status_code}")
        except Exception as e:
            print(f"❌ Failed to dispatch Discord webhook: {e}")
            
    elif slack_webhook:
        print("📤 Sending alert to Slack Webhook...")
        payload = {"text": message_content}
        try:
            r = requests.post(slack_webhook, json=payload)
            if r.status_code == 200:
                print("✅ Alert sent to Slack successfully.")
            else:
                print(f"⚠️ Slack Webhook returned code: {r.status_code}")
        except Exception as e:
            print(f"❌ Failed to dispatch Slack webhook: {e}")
            
    else:
        print("ℹ️ No webhook configured (DISCORD_WEBHOOK_URL or SLACK_WEBHOOK_URL).")
        print("Error details are printed in Actions console logs.")
        print(message_content)

if __name__ == "__main__":
    notify_failure()
