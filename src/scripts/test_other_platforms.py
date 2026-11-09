import os
from playwright.sync_api import sync_playwright

sites = [
    ("Synopsys", "https://careers.synopsys.com/job/bengaluru/intern/44408/95298114432"),
    ("Goldman Sachs", "https://higher.gs.com/roles/184192"),
    ("Harman", "https://jobsearch.harman.com/en_US/careers/JobDetail/Software-Engineer-CAN-UDS/32726"),
    ("Infor", "https://careers.infor.com/en/postings/0029cdab-7f9d-4a7c-b33a-c32a2fe77160")
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36")
    
    for name, url in sites:
        print(f"\n=== {name} ===")
        page = ctx.new_page()
        try:
            page.goto(url, wait_until="networkidle", timeout=20000)
            page.wait_for_timeout(2000)
            print("URL:", page.url)
            print("Title:", page.title())
            apply_btns = page.query_selector_all("a:has-text('Apply'), button:has-text('Apply')")
            print(f"Apply elements ({len(apply_btns)}):")
            for b in apply_btns[:3]:
                print("  Text:", b.inner_text().strip(), "Href:", b.get_attribute("href"), "Tag:", b.evaluate("el => el.tagName"))
        except Exception as e:
            print("Error:", e)
        finally:
            page.close()
            
    browser.close()
