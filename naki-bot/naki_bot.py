#!/usr/bin/env python3
"""
Naki AI Mascot Bot - Posts to Twitter/X for NakamaMesh.
Uses Gemini for tweets, images, hashtags. Posts 3x daily.
"""
import io
import random
import sys
from pathlib import Path

from google import genai
from google.genai import types

import config
from naki_prompts import (
    NAKI_MASCOT_IMAGE_PROMPT,
    TWEET_GENERATION_PROMPT,
    HASHTAG_GENERATION_PROMPT,
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

# Scene ideas for Naki images (match tweet themes)
SCENES = [
    "Naki floating happily next to a smartphone showing a mesh network diagram",
    "Naki in a relaxed pose with tiny Bluetooth icons around him",
    "Naki wearing his straw hat, surrounded by small glowing connection nodes",
    "Naki in a cozy scene with rain outside a window - representing disaster resilience",
    "Naki with a friendly wave, small $NAKI token symbols nearby",
    "Naki in a community scene with diverse people connected by lines",
    "Naki looking determined with a shield - representing unstoppable communication",
    "Naki relaxing with his hands behind his head, mesh network pattern in background",
]


def get_gemini_client():
    """Initialize Gemini client with API key."""
    if not config.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not set. Add it to .env or environment.")
    return genai.Client(api_key=config.GEMINI_API_KEY)


GEMINI_TEXT_MODELS = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.0-pro"]


def generate_tweet(client: genai.Client) -> str:
    """Generate a tweet using Gemini."""
    topic = random.choice(TOPICS)
    prompt = TWEET_GENERATION_PROMPT.format(topic=topic)
    for model in GEMINI_TEXT_MODELS:
        try:
            response = client.models.generate_content(model=model, contents=prompt)
            text = response.text.strip()
            break
        except Exception as e:
            print(f"{model} failed: {e}", file=sys.stderr)
            continue
    else:
        raise RuntimeError("All Gemini models failed")
    # Clean up any quotes or extra formatting
    if text.startswith('"') and text.endswith('"'):
        text = text[1:-1]
    return text[:275]  # Leave room for hashtags


def generate_hashtags(client: genai.Client, tweet: str) -> str:
    """Generate hashtags for the tweet."""
    prompt = HASHTAG_GENERATION_PROMPT.format(tweet=tweet)
    for model in GEMINI_TEXT_MODELS:
        try:
            response = client.models.generate_content(model=model, contents=prompt)
            return response.text.strip()
        except Exception as e:
            print(f"{model} failed: {e}", file=sys.stderr)
            continue
    return "#NakamaMesh #DePIN #MeshNetwork"  # Fallback


def generate_naki_image(client: genai.Client, tweet: str) -> bytes | None:
    """
    Generate an image of Naki using Gemini's native image generation.
    """
    scene = random.choice(SCENES)
    prompt = NAKI_MASCOT_IMAGE_PROMPT.format(scene_description=scene)
    # Add tweet context for relevance
    full_prompt = f"{prompt}\n\nThis image will accompany a tweet about: {tweet[:100]}"

    try:
        response = client.models.generate_content(
            model="imagen-3.0-generate-002",
            contents=full_prompt,
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
            ),
        )
    except Exception as e:
        print(f"Image generation failed: {e}", file=sys.stderr)
        return None

    # Extract image from response
    parts = getattr(response, "parts", None) or (
        getattr(response.candidates[0].content, "parts", []) if response.candidates else []
    )
    for part in parts:
        if getattr(part, "inline_data", None) is not None:
            return part.inline_data.data
    return None


def post_to_twitter(tweet: str, hashtags: str, image_bytes: bytes | None) -> bool:
    """Post tweet to Twitter/X using Tweepy."""
    if not all([
        config.TWITTER_API_KEY,
        config.TWITTER_API_SECRET,
        config.TWITTER_ACCESS_TOKEN,
        config.TWITTER_ACCESS_TOKEN_SECRET,
    ]):
        print("Twitter credentials not configured. Skipping post.", file=sys.stderr)
        return False

    import tweepy

    full_text = f"{tweet}\n\n{hashtags}"
    if len(full_text) > 280:
        full_text = f"{tweet}\n{hashtags}"[:280]

    client = tweepy.Client(
        consumer_key=config.TWITTER_API_KEY,
        consumer_secret=config.TWITTER_API_SECRET,
        access_token=config.TWITTER_ACCESS_TOKEN,
        access_token_secret=config.TWITTER_ACCESS_TOKEN_SECRET,
    )
    auth = tweepy.OAuth1UserHandler(
        config.TWITTER_API_KEY,
        config.TWITTER_API_SECRET,
        config.TWITTER_ACCESS_TOKEN,
        config.TWITTER_ACCESS_TOKEN_SECRET,
    )
    api = tweepy.API(auth)

    try:
        if image_bytes:
            img_file = io.BytesIO(image_bytes)
            img_file.name = "naki.png"
            media = api.media_upload(filename="naki.png", file=img_file)
            response = client.create_tweet(text=full_text, media_ids=[media.media_id])
        else:
            response = client.create_tweet(text=full_text)
        print(f"Posted successfully: {response.data['id']}")
        return True
    except Exception as e:
        print(f"Twitter post failed: {e}", file=sys.stderr)
        return False


def main():
    """Generate and post one Naki tweet."""
    print("Naki is thinking...")
    client = get_gemini_client()

    tweet = generate_tweet(client)
    print(f"Tweet: {tweet}")

    hashtags = generate_hashtags(client, tweet)
    print(f"Hashtags: {hashtags}")

    image_bytes = generate_naki_image(client, tweet)
    if image_bytes:
        print("Image generated!")
    else:
        print("No image (continuing without)")

    success = post_to_twitter(tweet, hashtags, image_bytes)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
