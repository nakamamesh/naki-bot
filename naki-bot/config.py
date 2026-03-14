"""Configuration for Naki AI Mascot Bot."""
import os
from dotenv import load_dotenv

load_dotenv()

# Gemini API (for tweets, images, hashtags, responses)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Twitter/X API - Get from https://developer.x.com/
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY", "")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET", "")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN", "")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "")

# Naki mascot identity
NAKI_DESCRIPTION = """
Naki is the AI mascot for NakamaMesh (https://nakamamesh.network/) - a decentralized mesh network for unstoppable communication.
Naki is a cute, cheerful pink axolotl wearing a straw hat with a red band. He has vibrant purple, blue, and magenta feathery gills.
He represents: community-owned infrastructure, disaster-resilient communication, DePIN, mesh networks, and "unstoppable communication for everyone."
"""
