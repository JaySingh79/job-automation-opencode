from playwright.sync_api import sync_playwright
import time

URL = "https://job-boards.greenhouse.io/doordashindia/jobs/5856393"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(URL, timeout=40000, wait_until="domcontentloaded")
    time.sleep(2)

    # Let's inspect candidate-location
    print("--- Candidate Location ---")
    inp = page.locator('[id="candidate-location"]')
    if inp.count() > 0:
        inp.first.click()
        time.sleep(0.5)
        # Type "Pune"
        inp.first.fill("Pune")
        time.sleep(1)
        opts = page.locator("[class*='-menu'] [id*='option'], [id*='listbox'] [id*='option']")
        print("Candidate-location options after typing 'Pune':", [opts.nth(i).inner_text().strip() for i in range(opts.count())])
        inp.first.fill("")
        time.sleep(0.5)
        inp.first.fill("India")
        time.sleep(1)
        opts = page.locator("[class*='-menu'] [id*='option'], [id*='listbox'] [id*='option']")
        print("Candidate-location options after typing 'India':", [opts.nth(i).inner_text().strip() for i in range(opts.count())])

    # Inspect question_46985241
    print("--- Question 46985241 (Worked at DoorDash) ---")
    inp = page.locator('[id="question_46985241"]')
    if inp.count() > 0:
        inp.first.click()
        time.sleep(0.5)
        opts = page.locator("[class*='-menu'] [id*='option'], [id*='listbox'] [id*='option']")
        print("Question 46985241 options:", [opts.nth(i).inner_text().strip() for i in range(opts.count())])

    # Inspect question_46985242
    print("--- Question 46985242 (Acknowledgement) ---")
    inp = page.locator('[id="question_46985242"]')
    if inp.count() > 0:
        inp.first.click()
        time.sleep(0.5)
        opts = page.locator("[class*='-menu'] [id*='option'], [id*='listbox'] [id*='option']")
        print("Question 46985242 options:", [opts.nth(i).inner_text().strip() for i in range(opts.count())])

    browser.close()
