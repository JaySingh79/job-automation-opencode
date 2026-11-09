from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://mahiruho.com/career", wait_until="domcontentloaded", timeout=20000)
    opts = page.locator("#designation option").all_inner_texts()
    vals = [o.get_attribute("value") for o in page.locator("#designation option").all()]
    print("Designation options:", list(zip(vals, opts)))
    page.close()
    browser.close()
