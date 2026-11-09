import time
import sys
import os
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(r"D:\Projects\PRACTICE\firecrawl_test")
URL = "https://job-boards.greenhouse.io/doordashindia/jobs/5856393"
RESUME_PATH = str(ROOT / "Resumes" / "Jay Resume GenAI+DS 5th Aug.pdf")

def run():
    print(f"Launching HEADED Chromium for DoorDash: {URL}")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--start-maximized", "--no-sandbox"]
        )
        context = browser.new_context(
            no_viewport=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        print("Navigating to DoorDash application page...")
        page.goto(URL, timeout=45000, wait_until="domcontentloaded")
        page.wait_for_selector("form", timeout=20000)
        time.sleep(2)

        # Inspect all form fields
        fields_info = page.evaluate('''() => {
            const inputs = Array.from(document.querySelectorAll('input, select, textarea, button[type="submit"]')).map(el => {
                const label = el.closest('div, label, fieldset')?.innerText || '';
                return {
                    tag: el.tagName,
                    type: el.type,
                    id: el.id,
                    name: el.name,
                    required: el.required || el.getAttribute('aria-required') === 'true',
                    label: label.split('\\n')[0].slice(0, 80)
                };
            });
            return inputs;
        }''')
        print(f"Discovered {len(fields_info)} controls:")
        for f in fields_info:
            print(f"  [{f['tag']}] id={f['id']} name={f['name']} type={f['type']} req={f['required']} label={f['label']}")

        browser.close()

if __name__ == "__main__":
    run()
