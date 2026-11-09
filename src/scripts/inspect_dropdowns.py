from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    
    # Check Flymedia dropdown options
    page1 = browser.new_page()
    page1.goto("https://flymediatech.com/apply-for-job/", wait_until="domcontentloaded", timeout=20000)
    select1 = page1.locator("select")
    if select1.count() > 0:
        opts1 = select1.first.locator("option").all_inner_texts()
        print("Flymedia job options:", opts1)
    page1.close()
    
    # Check Eulogik dropdown options
    page2 = browser.new_page()
    page2.goto("https://eulogik.com/careers", wait_until="domcontentloaded", timeout=20000)
    job_sel = page2.locator("#apply-job")
    if job_sel.count() > 0:
        opts2 = job_sel.locator("option").all_inner_texts()
        print("Eulogik job options:", opts2)
    exp_sel = page2.locator("#apply-experience")
    if exp_sel.count() > 0:
        opts_exp = exp_sel.locator("option").all_inner_texts()
        print("Eulogik exp options:", opts_exp)
    page2.close()
    
    browser.close()
