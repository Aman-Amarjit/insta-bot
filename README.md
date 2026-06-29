# Daily Facts Instagram Bot 🚀

A serverless, automated Instagram Daily Facts bot. It generates verified, surprising facts in daily-rotating categories using the Groq API, programmatically renders them into high-contrast minimalist infographics using Pillow, and publishes them twice daily to Instagram.

The workflow is orchestrated via **GitHub Actions** (using a cron scheduler) and stores history metadata in a **Supabase** cloud PostgreSQL database.

---

## Features
- **Serverless Automation**: Runs entirely within GitHub Actions free-tier runner limits.
- **Pillow Infographic Engine**: Dynamically creates 1080x1080 square JPGs. Implements auto-wrapping, margins, watermark overlay opacity, and dynamic font scaling (48px down to 24px) to prevent layout overflows.
- **Self-Balancing Schedule Calendar**: Rotates categories twice daily (9:00 AM and 6:00 PM IST) and self-balances category distribution to prevent repetitive posts.
- **Instagram Session Persistence**: Serializes authentication session cookies and updates them securely in the GitHub repository's secrets on each run to prevent login checkpoints/challenges.
- **Upfront Error Mitigations**: Retries JSON generation on parse errors, warns on invalid aspect ratios/sizes, and logs failures to Slack or Discord webhooks.

---

## Setup Instructions

### 1. Database Setup (Supabase)
1. Go to [Supabase Console](https://supabase.com/) and create a new project.
2. Go to the **SQL Editor** tab in the dashboard.
3. Paste and run the contents of the `schema.sql` file located in this repository. This creates the `posts` table and indexes.

### 2. Configure GitHub Secrets
1. Generate a GitHub **Personal Access Token (PAT)**:
   - Go to GitHub → Settings → Developer Settings → Personal Access Tokens (Classic).
   - Generate a token with the **`repo`** scope (which grants write permission to secrets). Copy it.
2. In your GitHub repository page, navigate to **Settings** → **Secrets and variables** → **Actions** → **New repository secret**.
3. Create the following secrets:

| Secret Name | Value Description |
| :--- | :--- |
| `GROQ_API_KEY` | Your Groq Console API Key |
| `INSTAGRAM_USERNAME` | Your Instagram username (`facts_giver_official`) |
| `INSTAGRAM_PASSWORD` | Your Instagram password (`Promethium@14561`) |
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_KEY` | Your Supabase Project API Key (`service_role` or secret key to bypass write RLS) |
| `GH_PAT` | The GitHub Personal Access Token generated in step 1 |
| `WATERMARK_TEXT` | (Optional) Infographic footer brand watermark (e.g. `@dailyfacts`) |
| `INSTAGRAM_SESSION` | (Optional) Leave empty initially. The bot will automatically create, base64-encode, and save the session here after the first run. |

### 3. Commit Fonts
Verify that the `fonts/` directory containing `Inter-Regular.ttf` and `Inter-Bold.ttf` is pushed to your GitHub repository. The Pillow engine loads these local files to render the images without internet dependencies.

### 4. Run the Bot
1. Go to the **Actions** tab of your GitHub repository.
2. Under "Workflows", select **Daily Facts Instagram Bot**.
3. Click the **Run workflow** dropdown and click the green **Run workflow** button.
4. Once completed, inspect the execution logs. Check your Instagram profile to view the published infographic, and check the Supabase `posts` table to verify metadata was stored correctly!
