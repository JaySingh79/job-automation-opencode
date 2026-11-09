"""
test_google_search_playwright.py — Search Google with &tbs=qdr:m for past month results.
"""
import urllib.parse
from playwright.sync_api import sync_playwright

def search_google(query, num_results=20):
    encoded_q = urllib.parse.quote_plus(query)
    # tbs=qdr:m filters for Past Month
    url = f"https://www.google.com/search?q={encoded_q}&tbs=qdr:m&num={num_results}"
    print(f"Navigating to: {url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=15000)
        page.wait_for_timeout(2000)

        # Check title
        title = page.title()
        print(f"Page title: {title}")

        # Extract search result links
        links = page.evaluate("""() => {
            const results = [];
            document.querySelectorAll('a[href]').forEach(a => {
                const href = a.href;
                if (href && (href.includes('ashbyhq.com') || href.includes('lever.co') || href.includes('greenhouse.io'))) {
                    const text = a.innerText.trim();
                    results.push({ url: href, text: text });
                }
            });
            return results;
        }""")

        browser.close()
        print(f"Extracted {len(links)} matching ATS links:")
        for l in links[:10]:
            print(f"  {l['url']} -> {l['text'][:60]}")
        return links

if __name__ == "__main__":
    q = 'site:jobs.ashbyhq.com ("India" OR "Remote") ("Machine Learning" OR "AI" OR "Python" OR "Software") -senior -lead'
    search_google(q)
