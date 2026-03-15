#!/usr/bin/env python3
"""
Naki AI Mascot Bot - Posts to Twitter/X for NakamaMesh.
Uses Gemini REST API directly. Posts 3x daily.
Bulletproof version - direct REST, no SDK dependency issues.
"""
import random
import sys
import time
import requests
import tweepy
import config
from naki_prompts import (
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

# Try these models in order until one works
MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
]

def call_gemini(prompt: str) -> str:
    """
    Call Gemini API directly via REST using v1beta endpoint.
    Tries multiple models with retry logic for rate limits.
    """
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": config.GEMINI_API_KEY,
    }
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 300,
            "temperature": 0.9,
        }
    }

    last_error = None
    for model in MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        try:
            print(f"Trying model: {model}", file=sys.stderr)
            response = requests.post(url, headers=headers, json=body, timeout=30)

            if response.status_code == 429:
                print(f"{model} rate limited, trying next...", file=sys.stderr)
                time.sleep(2)
                continue

            if response.status_code == 404:
                print(f"{model} not found, trying next...", file=sys.stderr)
                continue

            response.raise_for_status()
            data = response.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            print(f"Success with model: {model}", file=sys.stderr)
            return text

        except requests.exceptions.HTTPError as e:
            print(f"{model} HTTP error: {e}", file=sys.stderr)
            last_error = e
            continue
        except Exception as e:
            print(f"{model} error: {e}", file=sys.stderr)
            last_error = e
            continue

    raise RuntimeError(f"All Gemini models failed. Last error: {last_error}")


def generate_tweet() -> str:
    """Generate a tweet using Gemini."""
    topic = random.choice(TOPICS)
    prompt = TWEET_GENERATION_PROMPT.format(topic=topic)
    text = call_gemini(prompt)
    if text.startswith('"') and text.endswith('"'):
        text = text[1:-1]
    return text[:275]


def generate_hashtags(tweet: str) -> str:
    """Generate hashtags for the tweet."""
    try:
        prompt = HASHTAG_GENERATION_PROMPT.format(tweet=tweet)
        return call_gemini(prompt)
    except Exception as e:
        print(f"Hashtag generation failed, using defaults: {e}", file=sys.stderr)
        return "#NakamaMesh #DePIN #MeshNetwork #Solana #NAKI"


def post_to_twitter(tweet: str, hashtags: str) -> bool:
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
        response = twitter_client.create_tweet(text=full_text)
        print(f"Posted successfully! Tweet ID: {response.data['id']}")
        return True
    except Exception as e:
        print(f"Twitter post failed: {e}", file=sys.stderr)
        return False


def main():
    """Generate and post one Naki tweet."""
    print("Naki is thinking... 🦎")

    try:
        tweet = generate_tweet()
        print(f"Tweet: {tweet}")
    except Exception as e:
        print(f"Failed to generate tweet: {e}", file=sys.stderr)
        sys.exit(1)

    hashtags = generate_hashtags(tweet)
    print(f"Hashtags: {hashtags}")

    success = post_to_twitter(tweet, hashtags)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
