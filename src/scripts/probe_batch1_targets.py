import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(r"D:\Projects\PRACTICE\firecrawl_test")
BATCH_FILE = ROOT / "src" / "job_search_results" / "naukri" / "direct_company_platforms" / "batch_bigtech_custom.json"
PROGRESS_FILE = ROOT / "src" / "application_progress" / "direct_corporate" / "batch1_progress.json"
PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)

with open(BATCH_FILE, "r", encoding="utf-8") as f:
    batch_data = json.load(f)

jobs = batch_data.get("jobs", [])

print(f"Loaded {len(jobs)} jobs from batch_bigtech_custom.json")

# Let's inspect the first 5 target candidate jobs
test_targets = [
    jobs[0], # Flymedia Technology
    jobs[1], # Tesco
    jobs[2], # Google
    jobs[3], # Apple
    jobs[5], # Findoc
    jobs[9], # Interactive Brokers
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    for idx, target in enumerate(test_targets):
        co = target.get("company")
        title = target.get("title")
        url = target.get("company_site_url")
        print(f"\n--- Checking Target {idx+1}: [{co}] {title} ---")
        print(f"URL: {url}")
        
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        )
        try:
            resp = page.goto(url, wait_until="domcontentloaded", timeout=20000)
            time.sleep(2)
            page_title = page.title()
            current_url = page.url
            status = resp.status if resp else None
            print(f"Status: {status} | Title: {page_title}")
            print(f"Current URL: {current_url}")
            
            # Check for stale/404/expired
            content_lower = page.content().lower()
            is_expired = False
            for marker in ["job not found", "position is no longer available", "posting has expired", "job has expired", "no longer accepting applications", "404 not found", "page not found"]:
                if marker in content_lower:
                    is_expired = True
                    print(f"-> Expired marker detected: '{marker}'")
                    break
                    
            if is_expired:
                print("Result: EXPIRED / STALE")
                continue
                
            # Check for forms / inputs / apply button
            apply_btn = page.locator("a:has-text('Apply'), button:has-text('Apply'), a:has-text('Apply Now'), button:has-text('Apply Now'), input[value='Apply Now']")
            count_apply = apply_btn.count()
            print(f"Apply elements found: {count_apply}")
            
            inputs = page.locator("input:visible, textarea:visible, select:visible")
            print(f"Visible inputs/textareas/selects: {inputs.count()}")
            
        except Exception as e:
            print(f"Error checking {co}: {e}")
        finally:
            page.close()
            
    browser.close()
