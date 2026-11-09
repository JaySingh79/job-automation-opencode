"""
discover_more_gh.py
"""
import urllib.request
import json
import ssl
from concurrent.futures import ThreadPoolExecutor, as_completed

CTX = ssl.create_default_context()
UA = {"User-Agent": "Mozilla/5.0"}

ORGS = [
    "sprinklr", "zeta", "yugabyte", "cloudera", "nutanix", "freshworks",
    "deliveroo", "thoughtworks", "okta", "instacart", "doordash", "affirm",
    "airtel", "airtelx", "airtelafrica", "credgenics", "indiamart", "zomato",
    "blinkit", "lenskart", "nykaa", "pharmeasy", "1mg", "tatadigital",
    "cleartax", "blackbuck", "khatabook", "mpl", "dream11", "games24x7",
    "zetaapps", "zetaglobal", "zeta-interactive", "sprinklrinc", "freshdesk"
]

def check(o):
    u = f"https://boards-api.greenhouse.io/v1/boards/{o}/jobs"
    try:
        req = urllib.request.Request(u, headers=UA)
        with urllib.request.urlopen(req, timeout=5, context=CTX) as r:
            data = json.loads(r.read().decode("utf-8", "replace"))
            jobs = data.get("jobs", [])
            if jobs: return o, len(jobs)
    except Exception:
        pass
    return None

def main():
    with ThreadPoolExecutor(max_workers=20) as ex:
        futs = {ex.submit(check, o): o for o in ORGS}
        for f in as_completed(futs):
            res = f.result()
            if res:
                print(f"  [GH FOUND] {res[0]}: {res[1]} jobs")

if __name__ == "__main__":
    main()
