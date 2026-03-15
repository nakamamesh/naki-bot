#!/usr/bin/env python3
"""
Naki AI Mascot Bot - Posts to Twitter/X for NakamaMesh.
Uses Gemini REST API for tweets AND images. Posts 3x daily.
Bulletproof version - direct REST, no SDK issues.
"""
import base64
import random
import sys
import time
import requests
import tweepy
import config
from naki_prompts import (
    TWEET_GENERATION_PROMPT,
    HASHTAG_GENERATION_PROMPT,
    NAKI_MASCOT_IMAGE_PROMPT,
)

# Topic ideas for variety
TOPICS = [
    "NakamaMesh Bluetooth mesh - no internet needed",
    "DePIN and decentralized infrastructure",
    "Earning $NAKI by running relay nodes",
    "Disaster resilience - when cell towers fall",
    "Mesh networks for remote areas",
    "Community-owned communication",
    "End-to-end encrypted messaging without servers",
    "Typhoon disaster communication",
    "Unstoppable communication for everyone",
    "LoRa expansion roadmap",
    "100% open source mesh network",
    "Phone-to-phone messaging",
]

# Scene ideas for Naki images
SCENES = [
    "Naki floating happily next to a smartphone showing a mesh network diagram",
    "Naki in a relaxed pose with tiny Bluetooth icons glowing around him",
    "Naki wearing his straw hat, surrounded by small glowing connection nodes",
    "Naki in a cozy scene with rain and lightning outside - representing disaster resilience",
    "Naki with a friendly wave, small $NAKI token symbols floating nearby",
    "Naki in a community scene with diverse people connected by glowing lines",
    "Naki looking determined with a shield - representing unstoppable communication",
    "Naki relaxing with mesh network pattern glowing in the background",
    "Naki holding a tiny phone with signal waves radiating outward",
    "Naki on a rooftop with city skyline and mesh network lines connecting buildings",
]

# Text generation models to try in order
TEXT_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
]

GEMINI_HEADERS = {
    "Content-Type": "application/json",
}


def call_gemini_text(prompt: str) -> str:
    """Call Gemini text API directly via REST using v1beta."""
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": 300, "temperature": 0.9}
    }
    last_error = None
    for model in TEXT_MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        params = {"key": config.GEMINI_API_KEY}
        try:
            print(f"Trying text model: {model}", file=sys.stderr)
            resp = requests.post(url, headers=GEMINI_HEADERS, params=params, json=body, timeout=30)
            if resp.status_code == 429:
                print(f"{model} rate limited, trying next...", file=sys.stderr)
                time.sleep(2)
                continue
            if resp.status_code == 404:
                print(f"{model} not found, trying next...", file=sys.stderr)
                continue
            resp.raise_for_status()
            data = resp.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            print(f"Text success with: {model}", file=sys.stderr)
            return text
        except Exception as e:
            print(f"{model} error: {e}", file=sys.stderr)
            last_error = e
            continue
    raise RuntimeError(f"All text models failed. Last: {last_error}")


def call_gemini_image(prompt: str) -> bytes | None:
    """Generate image using gemini-2.5-flash-image via REST."""
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent"
    params = {"key": config.GEMINI_API_KEY}
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]}
    }
    try:
        print("Generating Naki image...", file=sys.stderr)
        resp = requests.post(url, headers=GEMINI_HEADERS, params=params, json=body, timeout=60)
        if resp.status_code in [429, 404, 403]:
            print(f"Image generation skipped: {resp.status_code}", file=sys.stderr)
            return None
        resp.raise_for_status()
        data = resp.json()
        # Extract image from response parts
        parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
        for part in parts:
            if "inlineData" in part:
                image_b64 = part["inlineData"]["data"]
                print("Image generated successfully!", file=sys.stderr)
                return base64.b64decode(image_b64)
        print("No image in response, continuing without image.", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Image generation failed (non-fatal): {e}", file=sys.stderr)
        return None


def generate_tweet() -> str:
    """Generate a tweet using Gemini."""
    topic = random.choice(TOPICS)
    prompt = TWEET_GENERATION_PROMPT.format(topic=topic)
    text = call_gemini_text(prompt)
    if text.startswith('"') and text.endswith('"'):
        text = text[1:-1]
    return text[:275]


def generate_hashtags(tweet: str) -> str:
    """Generate hashtags for the tweet."""
    try:
        prompt = HASHTAG_GENERATION_PROMPT.format(tweet=tweet)
        return call_gemini_text(prompt)
    except Exception as e:
        print(f"Hashtag generation failed, using defaults: {e}", file=sys.stderr)
        return "#NakamaMesh #DePIN #MeshNetwork #Solana #NAKI"


def generate_image(tweet: str) -> bytes | None:
    """Generate a Naki image for the tweet."""
    scene = random.choice(SCENES)
    prompt = NAKI_MASCOT_IMAGE_PROMPT.format(scene_description=scene)
    full_prompt = f"{prompt}\n\nThis image goes with a tweet about: {tweet[:100]}"
    return call_gemini_image(full_prompt)


def post_to_twitter(tweet: str, hashtags: str, image_bytes: bytes | None) -> bool:
    """Post tweet to Twitter/X using Tweepy."""
    if not all([
        config.TWITTER_API_KEY,
        config.TWITTER_API_SECRET,
        config.TWITTER_ACCESS_TOKEN,
        config.TWITTER_ACCESS_TOKEN_SECRET,
    ]):
        print("Twitter credentials not configured.", file=sys.stderr)
        return False

    full_text = f"{tweet}\n\n{hashtags}"
    if len(full_text) > 280:
        full_text = full_text[:280]

    twitter_client = tweepy.Client(
        consumer_key=config.TWITTER_API_KEY,
        consumer_secret=config.TWITTER_API_SECRET,
        access_token=config.TWITTER_ACCESS_TOKEN,
        access_token_secret=config.TWITTER_ACCESS_TOKEN_SECRET,
    )

    try:
        # Upload image if we have one
        media_ids = None
        if image_bytes:
            try:
                import io
                auth = tweepy.OAuth1UserHandler(
                    config.TWITTER_API_KEY,
                    config.TWITTER_API_SECRET,
                    config.TWITTER_ACCESS_TOKEN,
                    config.TWITTER_ACCESS_TOKEN_SECRET,
                )
                api_v1 = tweepy.API(auth)
                img_file = io.BytesIO(image_bytes)
                img_file.name = "naki.png"
                media = api_v1.media_upload(filename="naki.png", file=img_file)
                media_ids = [media.media_id]
                print(f"Image uploaded! Media ID: {media.media_id}", file=sys.stderr)
            except Exception as e:
                print(f"Image upload failed (posting without image): {e}", file=sys.stderr)
                media_ids = None

        # Post the tweet
        if media_ids:
            response = twitter_client.create_tweet(text=full_text, media_ids=media_ids)
        else:
            response = twitter_client.create_tweet(text=full_text)

        print(f"Posted successfully! Tweet ID: {response.data['id']}")
        return True
    except Exception as e:
        print(f"Twitter post failed: {e}", file=sys.stderr)
        return False


def main():
    """Generate and post one Naki tweet with image."""
    print("Naki is thinking... 🦎")

    # Generate tweet
    try:
        tweet = generate_tweet()
        print(f"Tweet: {tweet}")
    except Exception as e:
        print(f"Failed to generate tweet: {e}", file=sys.stderr)
        sys.exit(1)

    # Generate hashtags
    hashtags = generate_hashtags(tweet)
    print(f"Hashtags: {hashtags}")

    # Generate image (non-fatal if fails)
    image_bytes = generate_image(tweet)
    if image_bytes:
        print(f"Image ready: {len(image_bytes)} bytes")
    else:
        print("No image - posting text only")

    # Post to Twitter
    success = post_to_twitter(tweet, hashtags, image_bytes)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
