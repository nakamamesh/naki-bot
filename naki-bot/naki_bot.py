#!/usr/bin/env python3
"""
Naki AI Mascot Bot - Posts to Twitter/X for NakamaMesh.
Uses Gemini for tweets and hashtags. Posts 3x daily.
"""
import random
import sys

from google import genai
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


def generate_tweet() -> str:
    """Generate a tweet using Gemini."""
    client = genai.Client(api_key=config.GEMINI_API_KEY)
    topic = random.choice(TOPICS)
    prompt = TWEET_GENERATION_PROMPT.format(topic=topic)
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        text = response.text.strip()
        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1]
        return text[:275]
    except Exception as e:
        print(f"Gemini tweet generation failed: {e}", file=sys.stderr)
        raise RuntimeError(f"Tweet generation failed: {e}")


def generate_hashtags(tweet: str) -> str:
    """Generate hashtags for the tweet."""
    client = genai.Client(api_key=config.GEMINI_API_KEY)
    prompt = HASHTAG_GENERATION_PROMPT.format(tweet=tweet)
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        print(f"Hashtag generation failed: {e}", file=sys.stderr)
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

    tweet = generate_tweet()
    print(f"Tweet: {tweet}")

    hashtags = generate_hashtags(tweet)
    print(f"Hashtags: {hashtags}")

    success = post_to_twitter(tweet, hashtags)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
