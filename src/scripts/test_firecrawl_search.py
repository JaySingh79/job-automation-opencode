"""
test_firecrawl_search.py — Test Firecrawl search API with freshness.
"""
import os
import json
import urllib.request
import urllib.error
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("FIRECRAWL_API_KEY")

def firecrawl_search(query, limit=10):
    url = "https://api.firecrawl.dev/v1/search"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "query": query,
        "limit": limit,
        "scrapeOptions": {
            "formats": ["markdown"]
        }
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            results = data.get("data", [])
            return results
    except Exception as e:
        print(f"Firecrawl search error: {e}")
        return []

if __name__ == "__main__":
    queries = [
        'site:jobs.lever.co ("India" OR "Remote") ("Machine Learning" OR "AI Engineer" OR "Python" OR "Data") -senior after:2026-10-01',
        'site:job-boards.greenhouse.io OR site:boards.greenhouse.io ("India" OR "Remote") ("Machine Learning" OR "AI Engineer" OR "Software Engineer") -senior after:2026-10-01',
        'site:jobs.ashbyhq.com ("India" OR "Remote") ("Machine Learning" OR "AI Engineer" OR "Python") -senior after:2026-10-01'
    ]
    for q in queries:
        print(f"\nQuery: {q}")
        res = firecrawl_search(q, limit=5)
        print(f"Results: {len(res)}")
        for r in res:
            print(f"  [{r.get('title')}] -> {r.get('url')}")
