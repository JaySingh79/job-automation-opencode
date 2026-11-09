"""
test_search_engines.py — Test DuckDuckGo Lite, Bing, or others.
"""
import urllib.request
import urllib.parse
import re
import ssl

ctx = ssl.create_default_context()
ua = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def test_ddg_lite(q):
    data = urllib.parse.urlencode({"q": q}).encode()
    req = urllib.request.Request("https://lite.duckduckgo.com/lite/", data=data, headers=ua)
    try:
        with urllib.request.urlopen(req, timeout=10, context=ctx) as r:
            html = r.read().decode("utf-8", "replace")
            urls = re.findall(r'href="(https?://[^"]+)"', html)
            print(f"Lite DDG found {len(urls)} URLs")
            for u in urls[:5]:
                print("  ", u)
            return urls
    except Exception as e:
        print("Lite DDG Err:", e)
        return []

if __name__ == "__main__":
    test_ddg_lite('site:jobs.ashbyhq.com "India" "Engineer"')
