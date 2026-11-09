"""
discover_lever_orgs.py — Probe potential tech companies on Lever API.
"""
import urllib.request
import urllib.error
import json
import ssl
from concurrent.futures import ThreadPoolExecutor, as_completed

CTX = ssl.create_default_context()
UA = {"User-Agent": "Mozilla/5.0"}

LEVER_CANDIDATES = [
    "portcast", "drivetrain", "hevodata", "jobtwine", "enablecomp", "brillio-2",
    "offchainlabs", "farfetch", "equativ", "ewor", "policyme", "shyftlabs",
    "trackmind", "galepartners", "weekdayworks", "merklescience", "epifi",
    "lingarogroup", "zimperium", "outcomesai", "sprinto", "veeva", "binance",
    "everbridge", "gohighlevel", "paytm", "oscilar", "savvymoney", "teamsnap",
    "shopback-2", "saviynt", "smart-working-solutions", "greedygame", "slice",
    "khatabook", "bharatpe", "coindcx", "wazirx", "mpl", "dream11",
    "cars24", "spinny", "apna", "pratilipi", "sharechat", "glance",
    "vedantu", "cuemath", "classplus", "unacademy", "upgrad", "simplilearn",
    "atlassian", "coupa", "sendbird", "bolt", "ripple", "consensys",
    "supermove", "invideo", "browserstack", "clevertap", "curefit", "dunzo",
    "shadowfax", "porter", "rapido", "ola", "bounce", "yulu"
]

def check_lever(org):
    url = f"https://api.lever.co/v0/postings/{org}?mode=json"
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=5, context=CTX) as r:
            data = json.loads(r.read().decode("utf-8", "replace"))
            if isinstance(data, list) and len(data) > 0:
                return org, len(data)
    except Exception:
        pass
    return None

def main():
    print(f"Probing {len(LEVER_CANDIDATES)} candidate Lever orgs...")
    valid = {}
    with ThreadPoolExecutor(max_workers=25) as ex:
        futs = {ex.submit(check_lever, o): o for o in LEVER_CANDIDATES}
        for f in as_completed(futs):
            res = f.result()
            if res:
                org, count = res
                valid[org] = count
                print(f"  [FOUND] {org}: {count} jobs")

    print(f"\nDiscovered {len(valid)} active Lever boards:")
    print(sorted(valid.keys()))

if __name__ == "__main__":
    main()
