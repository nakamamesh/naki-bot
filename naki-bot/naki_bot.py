#!/usr/bin/env python3
"""
Naki AI Mascot Bot - Posts to Twitter/X for NakamaMesh.
Uses Gemini REST for text, Gemini SDK for images.
Posts 3x daily with Naki character images.
"""
import base64
import io
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

TEXT_MODELS = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
GEMINI_HEADERS = {"Content-Type": "application/json"}


def call_gemini_text(prompt: str) -> str:
    """Call Gemini text API via REST v1beta."""
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
            if resp.status_code in [429, 404]:
                print(f"{model} unavailable ({resp.status_code}), trying next...", file=sys.stderr)
                time.sleep(1)
                continue
            resp.raise_for_status()
            data = resp.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            print(f"Text success: {model}", file=sys.stderr)
            return text
        except Exception as e:
            print(f"{model} error: {e}", file=sys.stderr)
            last_error = e
            continue
    raise RuntimeError(f"All text models failed. Last: {last_error}")


def call_gemini_image(prompt: str) -> bytes | None:
    """
    Generate image using Gemini SDK (google-genai).
    Falls back gracefully if image generation fails.
    """
    try:
        from google import genai
        from google.genai import types

        print("Generating Naki image with SDK...", file=sys.stderr)
        client = genai.Client(api_key=config.GEMINI_API_KEY)

        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"]
            ),
        )

        # Extract image bytes from response
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                print("Image generated successfully!", file=sys.stderr)
                return part.inline_data.data

        print("No image found in SDK response.", file=sys.stderr)
        return None

    except Exception as e:
        print(f"Image generation failed (non-fatal): {e}", file=sys.stderr)
        return None


def generate_tweet() -> str:
    topic = random.choice(TOPICS)
    prompt = TWEET_GENERATION_PROMPT.format(topic=topic)
    text = call_gemini_text(prompt)
    if text.startswith('"') and text.endswith('"'):
        text = text[1:-1]
    return text[:275]


def generate_hashtags(tweet: str) -> str:
    try:
        prompt = HASHTAG_GENERATION_PROMPT.format(tweet=tweet)
        return call_gemini_text(prompt)
    except Exception as e:
        print(f"Hashtag generation failed, using defaults: {e}", file=sys.stderr)
        return "#NakamaMesh #DePIN #MeshNetwork #Solana #NAKI"


def generate_image(tweet: str) -> bytes | None:
    scene = random.choice(SCENES)
    prompt = NAKI_MASCOT_IMAGE_PROMPT.format(scene_description=scene)
    full_prompt = f"{prompt}\n\nThis image goes with a tweet about: {tweet[:100]}"
    return call_gemini_image(full_prompt)


def post_to_twitter(tweet: str, hashtags: str, image_bytes: bytes | None) -> bool:
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

    media_ids = None
    if image_bytes:
        try:
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

    try:
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
    print("Naki is thinking... 🦎")

    try:
        tweet = generate_tweet()
        print(f"Tweet: {tweet}")
    except Exception as e:
        print(f"Failed to generate tweet: {e}", file=sys.stderr)
        sys.exit(1)

    hashtags = generate_hashtags(tweet)
    print(f"Hashtags: {hashtags}")

    image_bytes = generate_image(tweet)
    if image_bytes:
        print(f"Image ready: {len(image_bytes)} bytes")
    else:
        print("No image - posting text only")

    success = post_to_twitter(tweet, hashtags, image_bytes)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
