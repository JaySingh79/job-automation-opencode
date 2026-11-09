import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(r"D:\Projects\PRACTICE\firecrawl_test")
SNAPSHOT_DIR = ROOT / "src" / "accessability_snapshot"

targets = [
    {
        "company": "Eulogik",
        "title": "Full-Stack Engineer - AI Platforms",
        "url": "https://eulogik.com/careers",
        "folder": "Eulogik"
    },
    {
        "company": "Perpetuity Capital",
        "title": "SOFTWARE ENGINEER",
        "url": "https://perpetuitycapital.in/careers",
        "folder": "Perpetuity_Capital"
    },
    {
        "company": "Flymedia Technology",
        "title": "Intern For AI/ML",
        "url": "https://flymediatech.com/current-job-opening/",
        "folder": "Flymedia_Technology"
    },
    {
        "company": "Tesco",
        "title": "Data Scientist",
        "url": "https://careers.tesco.com/en_GB/careers/JobDetail/Data-Scientist/140615",
        "folder": "Tesco"
    }
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    for t in targets:
        co = t["company"]
        print(f"\n=================== INSPECTING {co} ===================")
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        )
        try:
            page.goto(t["url"], wait_until="domcontentloaded", timeout=20000)
            time.sleep(3)
            
            # Save snapshot
            snap_path = SNAPSHOT_DIR / t["folder"]
            snap_path.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(snap_path / "page_landing.png"))
            print(f"Screenshot saved to {snap_path / 'page_landing.png'}")
            
            # Find forms and input elements
            forms = page.locator("form")
            print(f"Total forms: {forms.count()}")
            
            inputs = page.locator("input, textarea, select")
            count_inps = inputs.count()
            print(f"Total inputs/selects: {count_inps}")
            for i in range(min(count_inps, 15)):
                inp = inputs.nth(i)
                vis = inp.is_visible()
                tag = inp.evaluate("el => el.tagName.toLowerCase()")
                typ = inp.get_attribute("type") or ""
                name = inp.get_attribute("name") or ""
                inp_id = inp.get_attribute("id") or ""
                placeholder = inp.get_attribute("placeholder") or ""
                print(f"  [{i}] {tag} type={typ} name='{name}' id='{inp_id}' placeholder='{placeholder}' visible={vis}")
                
            # Check for Honeypots
            honeypots = page.locator("input[name*='honey'], input[id*='honey'], input[name*='beecatcher'], input[name*='EmailConfirm'], input[style*='display:none'], input[style*='visibility:hidden']")
            print(f"Honeypots detected: {honeypots.count()}")
            
            # Look for apply button / click apply if needed
            apply_btns = page.locator("a:has-text('Apply'), button:has-text('Apply'), a:has-text('Apply Now'), button:has-text('Apply Now')")
            print(f"Apply buttons: {apply_btns.count()}")
            for b in range(apply_btns.count()):
                txt = apply_btns.nth(b).inner_text().strip().replace('\n', ' ')
                href = apply_btns.nth(b).get_attribute("href") or ""
                print(f"  Btn [{b}]: text='{txt}' href='{href}'")
                
        except Exception as e:
            print(f"Error inspecting {co}: {e}")
        finally:
            page.close()
    browser.close()
