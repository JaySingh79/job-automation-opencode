from playwright.sync_api import sync_playwright

url = 'https://barclays.wd3.myworkdayjobs.com/External_Career_Site_Barclays/job/Pune-Gera-Commerzone-SEZ/Software-Engineer_JR-0000105230-3'

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url, wait_until='networkidle', timeout=25000)
    page.wait_for_timeout(3000)
    elements = page.query_selector_all("[data-automation-id]")
    print(f"Elements with data-automation-id: {len(elements)}")
    for el in elements:
        print(el.get_attribute("data-automation-id"), "->", el.inner_text().strip())
    browser.close()
