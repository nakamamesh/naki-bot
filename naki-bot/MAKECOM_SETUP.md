# Naki Bot - Make.com Alternative Setup

If you prefer Make.com over GitHub Actions, you can orchestrate Naki using Make.com scenarios.

## Option A: Make.com + Webhook (Recommended)

Host the Python script on a free service (Railway, Render, or a simple webhook) and trigger it from Make.com.

### 1. Deploy Script as Webhook

Use **Railway** (free tier) or **Render** (free tier):

- Create a simple Flask/FastAPI endpoint that runs `naki_bot.main()` when called
- Add a webhook URL that accepts POST requests
- Store secrets (GEMINI_API_KEY, Twitter credentials) as environment variables

### 2. Make.com Scenario

1. **Trigger**: Schedule (3x daily at your preferred times)
2. **Action**: HTTP - Make a request
   - URL: Your webhook URL
   - Method: POST
   - Headers: Optional auth header if you add one

### 3. For Comment Responses

- Create a second webhook for `respond_to_comments`
- Schedule it 1x daily (to conserve Twitter's 100 read/month limit)

## Option B: Make.com Native (No Code)

Make.com has Twitter and HTTP modules. You can:

1. **Schedule** → **HTTP (Gemini API)** → **Twitter Create Tweet**

### Tweet Generation via Gemini REST API

**HTTP Module 1 - Generate Tweet:**
- URL: `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={{GEMINI_API_KEY}}`
- Method: POST
- Body (JSON):
```json
{
  "contents": [{
    "parts": [{
      "text": "You are Naki, mascot for NakamaMesh. Generate ONE tweet about mesh networks or DePIN. Under 200 chars. Output only the tweet."
    }]
  }]
}
```

**HTTP Module 2 - Generate Image** (optional, uses Imagen):
- Requires separate Imagen API call - check [Gemini API docs](https://ai.google.dev/gemini-api/docs/imagen)

**Twitter Module - Create Post:**
- Connect your X/Twitter account
- Use the tweet text from HTTP Module 1
- Add hashtags: #NakamaMesh #DePIN #MeshNetwork

### Limitations

- Make.com free tier: 1,000 operations/month. 3 posts/day × 30 = 90 posts + 3 HTTP calls each = 270 ops/month for posting. Comment responses add more.
- Image generation via Make.com HTTP would need a separate scenario or a custom webhook (Python handles this better).

## Recommendation

**GitHub Actions** (included in this repo) is the simplest fully-free option:
- Unlimited minutes for public repos
- No Make.com operation limits
- All logic in one place
- Just add secrets and push

Use Make.com if you already have complex workflows there or prefer its UI.
