import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://mahiruho.com/career", wait_until="domcontentloaded", timeout=20000)
    time.sleep(2)
    print("Page title:", page.title())
    inputs = page.locator("input, textarea, select")
    print("Total inputs:", inputs.count())
    for i in range(inputs.count()):
        inp = inputs.nth(i)
        tag = inp.evaluate("el => el.tagName.toLowerCase()")
        typ = inp.get_attribute("type") or ""
        name = inp.get_attribute("name") or ""
        inp_id = inp.get_attribute("id") or ""
        placeholder = inp.get_attribute("placeholder") or ""
        vis = inp.is_visible()
        print(f"[{i}] {tag} type={typ} name='{name}' id='{inp_id}' placeholder='{placeholder}' vis={vis}")
    page.close()
    browser.close()
