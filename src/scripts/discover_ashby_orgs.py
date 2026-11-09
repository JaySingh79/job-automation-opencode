"""
discover_ashby_orgs.py — Probe potential tech and AI companies on Ashby API.
"""
import urllib.request
import urllib.error
import json
import ssl
from concurrent.futures import ThreadPoolExecutor, as_completed

CTX = ssl.create_default_context()
UA = {"User-Agent": "Mozilla/5.0"}

ASHBY_CANDIDATES = [
    "perplexity", "cohere", "mistral.ai", "fal-ai", "cartesia", "abridge",
    "gptzero", "tolken", "sarvam", "sarvam-ai", "playpowerlabs", "aiprise",
    "emergence", "jerry.ai", "sift", "tessera-labs", "gecko-robotics", "quora",
    "hex", "brainco", "notion", "skylo", "cynlr", "opslevel", "lgads",
    "sierra", "elevenlabs", "anysphere", "cursor", "cognition-labs", "cognition",
    "poolside", "decart", "baseten", "modal", "langfuse", "pinecone",
    "weaviate", "qdrant", "fireworks-ai", "groq", "characterai",
    "reka", "magic", "adept", "pika", "suno", "luma", "runway",
    "superhuman", "linear", "retool", "posthog", "resend", "clerk",
    "dub", "cal.com", "raycast", "warp", "modal-labs", "glean"
]

def check_ashby(org):
    url = f"https://api.ashbyhq.com/posting-api/job-board/{org}?includeCompensation=true"
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=5, context=CTX) as r:
            data = json.loads(r.read().decode("utf-8", "replace"))
            jobs = data.get("jobs", [])
            if jobs:
                return org, len(jobs)
    except Exception:
        pass
    return None

def main():
    print(f"Probing {len(ASHBY_CANDIDATES)} candidate Ashby orgs...")
    valid = {}
    with ThreadPoolExecutor(max_workers=25) as ex:
        futs = {ex.submit(check_ashby, o): o for o in ASHBY_CANDIDATES}
        for f in as_completed(futs):
            res = f.result()
            if res:
                org, count = res
                valid[org] = count
                print(f"  [FOUND] {org}: {count} jobs")

    print(f"\nDiscovered {len(valid)} active Ashby boards:")
    print(sorted(valid.keys()))

if __name__ == "__main__":
    main()
