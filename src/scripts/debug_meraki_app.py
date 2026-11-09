from playwright.sync_api import sync_playwright
import time
from pathlib import Path

ROOT = Path(r"D:\Projects\PRACTICE\firecrawl_test")
URL = "https://jobs.ashbyhq.com/meraki-labs/38e05386-b0ac-4c63-9780-5ec391a116be/application"
RESUME_PATH = str(ROOT / "Resumes" / "Jay Resume GenAI+DS 5th Aug.pdf")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(URL, timeout=40000, wait_until="networkidle")
    time.sleep(1)

    print("Title:", page.title())
    inputs = page.locator("input, textarea")
    print(f"Total inputs: {inputs.count()}")
    for i in range(inputs.count()):
        inp = inputs.nth(i)
        if inp.is_visible():
            name = inp.get_attribute("name") or inp.get_attribute("id") or inp.get_attribute("type")
            lbl = inp.evaluate("(el) => el.closest('div,label')?.innerText || ''").strip().replace("\n", " ")
            print(f"  Input: name='{name}' label='{lbl[:50]}'")

    page.screenshot(path=str(ROOT / "src" / "accessability_snapshot" / "meraki_form.png"), full_page=True)
    browser.close()
