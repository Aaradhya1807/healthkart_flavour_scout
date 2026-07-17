import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")
BASE_URL = "https://www.googleapis.com/youtube/v3"

# YouTube's commentThreads.list endpoint caps maxResults at 100 per request.
MAX_RESULTS_PER_REQUEST = 100


def search_videos(query, max_results=5):
    """
    Search YouTube videos based on a query.
    Returns a list of video IDs, or [] if the API key is missing or the
    request fails (so callers can fall back gracefully instead of crashing).
    """
    if not API_KEY:
        return []

    url = f"{BASE_URL}/search"
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
        "key": API_KEY,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"YouTube search failed: {e}")
        return []

    return [item["id"]["videoId"] for item in data.get("items", []) if "videoId" in item.get("id", {})]


def fetch_comments(video_id, max_comments=100):
    """
    Fetch top-level comments from a YouTube video.
    """
    max_comments = min(max_comments, MAX_RESULTS_PER_REQUEST)

    url = f"{BASE_URL}/commentThreads"
    params = {
        "part": "snippet",
        "videoId": video_id,
        "maxResults": max_comments,
        "textFormat": "plainText",
        "key": API_KEY,
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    comments = []
    for item in data.get("items", []):
        snippet = item.get("snippet", {}).get("topLevelComment", {}).get("snippet", {})
        text = snippet.get("textDisplay")
        if not text:
            continue
        comments.append({
            "platform": "youtube",
            "video_id": video_id,
            "text": text,
            "likes": snippet.get("likeCount", 0),
            "published_at": snippet.get("publishedAt"),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        })

    return comments


def fetch_comments_by_query(query, max_videos=3, max_comments_per_video=10):
    """
    Search videos by query and fetch comments from each video.
    Returns [] on any failure (missing key, quota exceeded, comments
    disabled on all matched videos, etc.) rather than raising, so the
    caller can fall back to sample data.
    """
    if not API_KEY:
        print("YOUTUBE_API_KEY not set — skipping live YouTube fetch.")
        return []

    video_ids = search_videos(query, max_videos)

    all_comments = []
    for vid in video_ids:
        try:
            comments = fetch_comments(vid, max_comments_per_video)
            all_comments.extend(comments)
        except requests.exceptions.RequestException as e:
            # Common cause: comments disabled on this video (403), or quota exceeded.
            print(f"Failed fetching comments for video {vid}: {e}")

    return all_comments