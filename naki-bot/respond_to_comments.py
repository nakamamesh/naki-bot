#!/usr/bin/env python3
"""
Naki AI Mascot Bot - Auto-respond to comments/mentions on Twitter.
Uses Gemini to generate friendly, on-brand replies.
Note: Twitter free tier has 100 read requests/month - run sparingly (e.g. 1x daily).
"""
import json
import os
import sys
from pathlib import Path

import config
from naki_prompts import COMMENT_RESPONSE_PROMPT


# File to track which comments we've already replied to
REPLIED_FILE = Path(__file__).parent / ".replied_comments.json"


def load_replied_ids() -> set[str]:
    """Load set of comment IDs we've already replied to."""
    if REPLIED_FILE.exists():
        try:
            data = json.loads(REPLIED_FILE.read_text())
            return set(data.get("ids", []))
        except Exception:
            pass
    return set()


def save_replied_id(comment_id: str):
    """Record that we've replied to this comment."""
    replied = load_replied_ids()
    replied.add(comment_id)
    # Keep only last 500 to avoid file bloat
    ids = list(replied)[-500:]
    REPLIED_FILE.write_text(json.dumps({"ids": ids}))


def get_gemini_client():
    """Initialize Gemini client."""
    if not config.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not set.")
    from google import genai
    return genai.Client(api_key=config.GEMINI_API_KEY)


def generate_reply(client, comment: str) -> str:
    """Generate a Naki-style reply using Gemini."""
    prompt = COMMENT_RESPONSE_PROMPT.format(comment=comment)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )
    return response.text.strip()[:275]


def main():
    """Check for new mentions/replies and respond."""
    if not all([
        config.TWITTER_API_KEY,
        config.TWITTER_API_SECRET,
        config.TWITTER_ACCESS_TOKEN,
        config.TWITTER_ACCESS_TOKEN_SECRET,
    ]):
        print("Twitter credentials not configured.", file=sys.stderr)
        sys.exit(1)

    import tweepy

    client = tweepy.Client(
        consumer_key=config.TWITTER_API_KEY,
        consumer_secret=config.TWITTER_API_SECRET,
        access_token=config.TWITTER_ACCESS_TOKEN,
        access_token_secret=config.TWITTER_ACCESS_TOKEN_SECRET,
    )

    # Get authenticated user's ID
    me = client.get_me()
    if not me.data:
        print("Could not get authenticated user.", file=sys.stderr)
        sys.exit(1)
    my_id = me.data.id

    # Fetch mentions (uses 1 read request)
    try:
        mentions = client.get_users_mentions(
            id=my_id,
            max_results=10,
            tweet_fields=["created_at", "conversation_id"],
            expansions=["referenced_tweets.id"],
        )
    except Exception as e:
        print(f"Failed to fetch mentions: {e}", file=sys.stderr)
        sys.exit(1)

    if not mentions.data:
        print("No new mentions.")
        sys.exit(0)

    replied_ids = load_replied_ids()
    gemini = get_gemini_client()
    new_replies = 0

    for tweet in mentions.data:
        if tweet.id in replied_ids:
            continue
        # Skip if we're replying to ourselves
        if tweet.author_id == my_id:
            continue

        comment_text = tweet.text
        if not comment_text or len(comment_text) < 2:
            continue

        try:
            reply_text = generate_reply(gemini, comment_text)
            response = client.create_tweet(
                text=reply_text,
                in_reply_to_tweet_id=tweet.id,
            )
            save_replied_id(tweet.id)
            new_replies += 1
            print(f"Replied to {tweet.id}: {reply_text[:50]}...")
        except Exception as e:
            print(f"Failed to reply to {tweet.id}: {e}", file=sys.stderr)

    print(f"Replied to {new_replies} new comment(s).")


if __name__ == "__main__":
    main()
