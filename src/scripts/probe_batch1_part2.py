import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(r"D:\Projects\PRACTICE\firecrawl_test")
BATCH_FILE = ROOT / "src" / "job_search_results" / "naukri" / "direct_company_platforms" / "batch_bigtech_custom.json"

with open(BATCH_FILE, "r", encoding="utf-8") as f:
    batch_data = json.load(f)

jobs = batch_data.get("jobs", [])

# Let's inspect jobs 25 to 65
test_targets = jobs[25:65]

results = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    for idx, target in enumerate(test_targets):
        co = target.get("company")
        title = target.get("title")
        url = target.get("company_site_url")
        exp = target.get("experience")
        domain = target.get("ats_domain")
        
        # Rule filter
        skills = [s.lower() for s in target.get("skills", [])]
        skills_str = " ".join(skills)
        if ("java" in skills_str or "c++" in skills_str) and "python" not in skills_str and "machine learning" not in skills_str and "ai" not in skills_str:
            continue
            
        if any(w in title.lower() for w in ["senior", "sr.", "lead", "staff", "principal", "architect", "manager", "director"]):
            continue
            
        if "wordpress" in title.lower() or "php" in title.lower() or "unity" in title.lower():
            continue
            
        print(f"\nChecking #{idx+26} [{co}] {title} ({exp}) -> {url}")
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        )
        try:
            resp = page.goto(url, wait_until="domcontentloaded", timeout=12000)
            time.sleep(2)
            page_title = page.title()
            current_url = page.url
            content_lower = page.content().lower()
            
            is_expired = False
            for marker in ["job not found", "position is no longer available", "posting has expired", "job has expired", "no longer accepting applications", "404 not found", "page not found"]:
                if marker in content_lower:
                    is_expired = True
                    break
                    
            if is_expired:
                print(f"-> Expired / Closed")
                continue
                
            apply_btn = page.locator("a:has-text('Apply'), button:has-text('Apply'), a:has-text('Apply Now'), button:has-text('Apply Now')")
            inputs = page.locator("input:visible, textarea:visible, select:visible")
            
            print(f"-> OK | Status: {resp.status if resp else None} | Apply btns: {apply_btn.count()} | Inputs: {inputs.count()} | Title: {page_title}")
            results.append({
                "job_id": target.get("job_id"),
                "company": co,
                "title": title,
                "url": url,
                "current_url": current_url,
                "page_title": page_title,
                "apply_count": apply_btn.count(),
                "inputs_count": inputs.count()
            })
        except Exception as e:
            print(f"-> Skip/Error: {e}")
        finally:
            page.close()
            
    browser.close()

with open(r"src/scripts/probe_results_batch1_part2.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print("\nDone. Saved to src/scripts/probe_results_batch1_part2.json")
