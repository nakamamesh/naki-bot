# Naki AI Mascot Bot

Naki is the AI mascot for [NakamaMesh](https://nakamamesh.network/) — a decentralized mesh network for unstoppable communication. This bot posts to Twitter/X 3 times daily with AI-generated tweets, images, hashtags, and auto-responds to comments.

## Features

- **3 posts per day** — Tweets about NakamaMesh, mesh networks, DePIN, use cases, news
- **AI-generated images** — Naki (pink axolotl mascot) in themed scenes via Gemini
- **Smart hashtags** — Auto-generated per tweet (#NakamaMesh, #DePIN, etc.)
- **Auto-respond to comments** — Friendly, on-brand replies via Gemini
- **100% free** — Gemini free tier, Twitter free tier, GitHub Actions (unlimited for public repos)

## Quick Start

### 1. Get API Keys

- **Gemini**: [Google AI Studio](https://aistudio.google.com/app/apikey) — free, 500 images/day
- **Twitter/X**: [Developer Portal](https://developer.x.com/) — free tier: 17 posts/day, 500/month

### 2. Configure

```bash
cd naki-bot
cp .env.example .env
# Edit .env with your keys
```

### 3. Test Locally

```bash
pip install -r requirements.txt
python naki_bot.py          # Post one tweet
python respond_to_comments.py  # Check & reply to comments
```

### 4. Deploy to GitHub Actions (Free Cloud Hosting)

1. Create a **public** GitHub repo (unlimited free Actions minutes)
2. Copy the `naki-bot` folder and `.github/workflows` into it
3. Add secrets: **Settings → Secrets and variables → Actions**
   - `GEMINI_API_KEY`
   - `TWITTER_API_KEY`
   - `TWITTER_API_SECRET`
   - `TWITTER_ACCESS_TOKEN`
   - `TWITTER_ACCESS_TOKEN_SECRET`
4. Push — workflows run automatically on schedule

**Schedule:**
- Posts: 8:00, 14:00, 20:00 UTC (3x daily)
- Comments: 12:30 UTC (1x daily — Twitter free tier has 100 reads/month)

### 5. Make.com Alternative

See [MAKECOM_SETUP.md](MAKECOM_SETUP.md) for Make.com workflow options.

## Project Structure

```
naki-bot/
├── naki_bot.py           # Main posting script
├── respond_to_comments.py # Comment reply script
├── naki_prompts.py       # Gemini prompts
├── config.py             # Config from .env
├── requirements.txt
├── .env.example
└── README.md
```

## Naki's Personality

Naki is a friendly, cheerful pink axolotl with a straw hat. He speaks for NakamaMesh's mission: unstoppable communication for everyone — no internet, no servers, no censorship. Community-owned. Disaster-resilient.

## Limits & Costs

| Service        | Free Tier                    |
|----------------|------------------------------|
| Gemini         | 500 images/day, 15 RPM       |
| Twitter        | 17 posts/day, 100 reads/month|
| GitHub Actions | Unlimited (public repos)     |

## Security Note

**Never commit your API keys.** Use `.env` locally and GitHub Secrets for Actions. The `.env` file is gitignored. If you've shared a key in chat or elsewhere, rotate it at [Google AI Studio](https://aistudio.google.com/app/apikey) or [Twitter Developer Portal](https://developer.x.com/).
