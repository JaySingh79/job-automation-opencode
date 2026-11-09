"""
test_search_methods.py — Test automated search engines for recent ATS jobs.
"""
import urllib.request
import urllib.parse
import json
import re
import ssl

CTX = ssl.create_default_context()
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}

def test_duckduckgo_html(query):
    print(f"\n--- Testing DuckDuckGo for: {query} ---")
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=10, context=CTX) as r:
            html = r.read().decode("utf-8", "replace")
            # Extract links
            links = re.findall(r'href="(/l/\?uddg=[^"]+)"', html)
            direct_urls = []
            for l in links:
                m = re.search(r'uddg=([^&]+)', l)
                if m:
                    u = urllib.parse.unquote(m.group(1))
                    direct_urls.append(u)
            print(f"Found {len(direct_urls)} URLs from DuckDuckGo HTML:")
            for u in direct_urls[:5]:
                print(f"  {u}")
            return direct_urls
    except Exception as e:
        print(f"ERR: {e}")
        return []

if __name__ == "__main__":
    q = 'site:jobs.ashbyhq.com ("India" OR "Remote") ("Machine Learning" OR "AI" OR "Python") -senior'
    test_duckduckgo_html(q)
