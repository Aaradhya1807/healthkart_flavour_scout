import requests
import pandas as pd

def fetch_reddit_comments(keyword="protein flavor", limit=100):
    url = "https://api.pushshift.io/reddit/search/comment/"

    params = {
        "q": keyword,
        "size": limit,
        "lang": "en"
    }

    response = requests.get(url, params=params, timeout=10)

    if response.status_code != 200:
        return pd.DataFrame({"comment": []})

    data = response.json().get("data", [])

    comments = []
    for item in data:
        body = item.get("body", "")
        if body and len(body) > 20:
            comments.append(body)

    return pd.DataFrame({"comment": comments})
