import os
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")

if not API_KEY:
    raise ValueError("YOUTUBE_API_KEY not found in environment variables")

BASE_URL = "https://www.googleapis.com/youtube/v3"


def search_videos(query, max_results=5):
    """
    Search YouTube videos based on a query
    Returns a list of video IDs
    """
    url = f"{BASE_URL}/search"
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
        "key": API_KEY
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    return [item["id"]["videoId"] for item in data.get("items", [])]


def fetch_comments(video_id, max_comments=500):
    """
    Fetch top-level comments from a YouTube video
    """
    url = f"{BASE_URL}/commentThreads"
    params = {
        "part": "snippet",
        "videoId": video_id,
        "maxResults": max_comments,
        "textFormat": "plainText",
        "key": API_KEY
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    comments = []
    for item in data.get("items", []):
        snippet = item["snippet"]["topLevelComment"]["snippet"]
        comments.append({
            "platform": "youtube",
            "video_id": video_id,
            "text": snippet["textDisplay"],
            "likes": snippet["likeCount"],
            "published_at": snippet["publishedAt"],
            "fetched_at": datetime.utcnow().isoformat()
        })

    return comments


def fetch_comments_by_query(query, max_videos=3, max_comments_per_video=10):
    """
    Search videos by query and fetch comments from each video
    """
    video_ids = search_videos(query, max_videos)

    all_comments = []
    for vid in video_ids:
        try:
            comments = fetch_comments(vid, max_comments_per_video)
            all_comments.extend(comments)
        except Exception as e:
            print(f"Failed fetching comments for video {vid}: {e}")

    return all_comments
