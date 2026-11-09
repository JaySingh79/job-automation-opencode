from playwright.sync_api import sync_playwright
import time

URL = "https://job-boards.greenhouse.io/doordashindia/jobs/5856393"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(URL, timeout=40000, wait_until="domcontentloaded")
    time.sleep(2)

    inp = page.locator('[id="candidate-location"]')
    if inp.count() > 0:
        inp.first.click()
        time.sleep(0.3)
        page.keyboard.type("Pune", delay=120)
        time.sleep(2)
        opts = page.locator("[class*='-menu'] [id*='option'], [id*='listbox'] [id*='option'], div[role='option']")
        print("Candidate-location options after keyboard typing 'Pune':", [opts.nth(i).inner_text().strip() for i in range(opts.count())])

    browser.close()
