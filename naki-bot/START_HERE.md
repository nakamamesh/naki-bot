# Naki Bot — Start Instructions

Follow these steps exactly to launch the Naki AI mascot bot for free.

---

## Step 1: Get Your API Keys

### Gemini (free)
1. Go to https://aistudio.google.com/app/apikey  
2. Sign in with Google  
3. Click **Create API Key**  
4. Copy the key (starts with `AIza...`)

### Twitter/X (free)
1. Go to https://developer.x.com/  
2. Sign in → **Developer Portal**  
3. Create a project and app (or use existing)  
4. In your app → **Keys and tokens**  
5. Generate/copy:
   - **API Key** (Consumer Key)  
   - **API Key Secret** (Consumer Secret)  
   - **Access Token**  
   - **Access Token Secret**  
6. Set app permissions to **Read and write** (for posting)

---

## Step 2: Create a GitHub Repo

1. Go to https://github.com/new  
2. Name it (e.g. `naki-bot`)  
3. Set to **Public**  
4. Do **not** initialize with README  
5. Click **Create repository**

---

## Step 3: Upload the Bot Files

1. In your new repo, click **Add file** → **Upload files**  
2. Drag and drop these folders/files from your `Scraper` project:
   - `naki-bot` (entire folder: all files inside)
   - `.github` (entire folder, including `workflows` inside)
3. Click **Commit changes**

**Or** if you use Git locally:
```bash
cd /Users/i.j.maha/Scraper
git init
git add naki-bot .github
git commit -m "Add Naki bot"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

---

## Step 4: Add Secrets to GitHub

1. In your repo, go to **Settings** → **Secrets and variables** → **Actions**  
2. Click **New repository secret**  
3. Add each secret:

| Name | Value |
|------|-------|
| `GEMINI_API_KEY` | Your Gemini API key |
| `TWITTER_API_KEY` | Your Twitter API Key |
| `TWITTER_API_SECRET` | Your Twitter API Key Secret |
| `TWITTER_ACCESS_TOKEN` | Your Twitter Access Token |
| `TWITTER_ACCESS_TOKEN_SECRET` | Your Twitter Access Token Secret |

---

## Step 5: Run the Bot

The bot runs automatically on schedule:
- **3 posts per day** at 8:00, 14:00, 20:00 UTC  
- **1 comment check per day** at 12:30 UTC  

To run a post **right now** (manual test):
1. Go to **Actions** tab in your repo  
2. Click **Naki Post** in the left sidebar  
3. Click **Run workflow** → **Run workflow**  
4. Wait ~30–60 seconds, then refresh — you should see a new tweet on your account  

---

## Done

Your Naki bot is live. It will post 3 times per day and reply to comments once per day. No costs, no Make.com, all on GitHub.
