from playwright.sync_api import sync_playwright

url = "https://barclays.wd3.myworkdayjobs.com/External_Career_Site_Barclays/job/Pune-Gera-Commerzone-SEZ/Software-Engineer_JR-0000105230-3/apply"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url, wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(3000)
    print("Final URL:", page.url)
    print("Title:", page.title())
    buttons = page.query_selector_all("a, button")
    print(f"Interactive elements: {len(buttons)}")
    for b in buttons:
        txt = b.inner_text().strip()
        aid = b.get_attribute("data-automation-id")
        if txt or aid:
            print(f"  [{aid}] text='{txt}'")
    browser.close()
