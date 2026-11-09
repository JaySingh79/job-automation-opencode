from playwright.sync_api import sync_playwright

url = "https://jobsearch.harman.com/en_US/careers/ApplicationMethods?jobId=32726"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url, wait_until='domcontentloaded', timeout=20000)
    page.wait_for_timeout(2000)
    
    # Check all elements with class or text related to upload
    els = page.query_selector_all(".upload-option, .file-upload, [id*='upload'], [class*='upload']")
    for e in els:
        print(f"Tag: {e.evaluate('el => el.tagName')} | ID: {e.get_attribute('id')} | Class: {e.get_attribute('class')} | Visible: {e.is_visible()} | Text: {e.inner_text().strip()}")
    browser.close()
