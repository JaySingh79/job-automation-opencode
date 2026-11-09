from playwright.sync_api import sync_playwright

urls = [
    ("cloudsek", "https://job-boards.greenhouse.io/cloudsek/jobs/6222340004"),
    ("interview-kickstart", "https://jobs.ashbyhq.com/interview-kickstart/bf2a4802-4180-440b-b5bf-5f8058e69846"),
    ("coherehealth", "https://job-boards.greenhouse.io/coherehealth/jobs/7693298003"),
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    for name, url in urls:
        page = browser.new_page()
        page.goto(url, timeout=30000, wait_until="domcontentloaded")
        print(f"=== {name} ({page.url}) ===")
        print(f"Title: {page.title()}")
        body = page.locator("body").inner_text()[:400].replace("\n", " ")
        print(f"Body snippet: {body}")
        
        # Check buttons
        btns = page.locator("button, input[type='submit'], a.button, [role='button']")
        btn_texts = [btns.nth(i).inner_text().strip() for i in range(min(15, btns.count()))]
        print(f"Buttons: {btn_texts}")
        
        # Check if expired or 404
        if "no longer available" in body.lower() or "job not found" in body.lower() or "expired" in body.lower():
            print("  --> EXPIRED / CLOSED")
        page.close()
    browser.close()
