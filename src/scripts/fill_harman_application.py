import os
import time
from playwright.sync_api import sync_playwright

def fill_harman():
    url = "https://jobsearch.harman.com/en_US/careers/ApplicationMethods?jobId=32726"
    resume_path = r"D:\Projects\PRACTICE\firecrawl_test\Resumes\Jay Resume GenAI+DS 5th Aug.pdf"
    screenshot_dir = r"src\accessability_snapshot\Harman"
    os.makedirs(screenshot_dir, exist_ok=True)
    screenshot_path = os.path.join(screenshot_dir, "harman_staged_form.png")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
        )
        page = ctx.new_page()
        
        print(f"Navigating to {url}...")
        page.goto(url, wait_until="domcontentloaded", timeout=25000)
        page.wait_for_timeout(2500)
        
        # Step 1: Upload resume
        print("Uploading resume to Avature...")
        file_input = page.locator("input[type='file']")
        if file_input.count() > 0:
            file_input.first.set_input_files(resume_path)
            time.sleep(3.0)
            print("File set. Checking for Continue button...")
            continue_btn = page.locator("button:has-text('Continue'), a:has-text('Continue'), input[value='Continue']")
            if continue_btn.count() > 0:
                continue_btn.first.click()
                time.sleep(4.0)
                print("Navigated to Step 2 URL:", page.url)
        else:
            print("No file input found directly. Inspecting page elements...")
            
        print("Current page title:", page.title())
        print("Current page body excerpt:", page.inner_text("body")[:800])
        
        # Check inputs on Step 2
        inputs = page.query_selector_all("input, select, textarea")
        print(f"Inputs found: {len(inputs)}")
        for inp in inputs:
            itype = inp.get_attribute("type")
            name = inp.get_attribute("name") or inp.get_attribute("id")
            vis = inp.is_visible()
            val = inp.get_attribute("value") or ""
            print(f"  [{itype}] name='{name}' visible={vis} val='{val}'")
            
        browser.close()

if __name__ == "__main__":
    fill_harman()
