import os
import time
from playwright.sync_api import sync_playwright

def stage_harman():
    url = "https://jobsearch.harman.com/en_US/careers/ApplicationMethods?jobId=32726"
    resume_path = r"D:\Projects\PRACTICE\firecrawl_test\Resumes\Jay Resume GenAI+DS 5th Aug.pdf"
    screenshot_dir = r"src\accessability_snapshot\Harman"
    os.makedirs(screenshot_dir, exist_ok=True)
    screenshot_path = os.path.join(screenshot_dir, "harman_review_staged.png")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36")
        page = ctx.new_page()
        
        print("Navigating to Harman...")
        page.goto(url, wait_until="domcontentloaded", timeout=25000)
        page.wait_for_timeout(2000)
        
        # Step 1: Upload resume
        print("Step 1: Uploading resume...")
        with page.expect_file_chooser() as fc_info:
            page.locator("#methodButton--file").click()
        file_chooser = fc_info.value
        file_chooser.set_files(resume_path)
        page.wait_for_timeout(3000)
        
        page.locator("#uploadFileResume").click()
        page.wait_for_timeout(5000)
        print("Navigated to Step 2:", page.url)
        
        # Step 2: Fill required fields
        print("Step 2: Filling personal and general information...")
        
        # Phone
        phone_input = page.locator("input[name='1246']")
        if phone_input.count() > 0:
            phone_input.fill("+918651274328")
            time.sleep(0.5)
            
        # Preferred Name: No
        page.locator("select[name='1269']").select_option(label="No")
        time.sleep(0.5)
        
        # Country: India
        page.locator("select[name='1247']").select_option(label="India")
        time.sleep(0.5)
        
        # Source
        page.locator("select[name='1252']").select_option(label="HARMAN Careers Site / Job Alert")
        time.sleep(0.5)
        
        # Relatives: No
        page.locator("select[name='1254']").select_option(label="No")
        time.sleep(0.5)
        
        # Work Ex 1 (Pascal AI Labs): Location & Description & Currently work here
        if page.locator("input[name='1260-10-0']").count() > 0:
            page.locator("input[name='1260-10-0']").fill("Bengaluru, India")
        if page.locator("select[name='1260-6-0']").count() > 0:
            page.locator("select[name='1260-6-0']").select_option(label="Yes")
        desc0 = page.locator("textarea[name='1260-8-0']")
        if desc0.count() > 0:
            desc0.fill("Building production GenAI and agentic automation pipelines with Python.")
            
        # Work Ex 2 (Innovaccer): Location & Description & Currently work here
        if page.locator("input[name='1260-10-1']").count() > 0:
            page.locator("input[name='1260-10-1']").fill("Noida, India")
        if page.locator("select[name='1260-6-1']").count() > 0:
            page.locator("select[name='1260-6-1']").select_option(label="No")
        desc1 = page.locator("textarea[name='1260-8-1']")
        if desc1.count() > 0:
            desc1.fill("Data Science Intern working on healthcare data analytics.")
            
        # Education: Degree -> Bachelors
        if page.locator("select[name='1262-8-0']").count() > 0:
            page.locator("select[name='1262-8-0']").select_option(label="Bachelors")
            time.sleep(0.5)
            
        # Language: English -> Fluent
        if page.locator("select[name='1264-4-0']").count() > 0:
            page.locator("select[name='1264-4-0']").select_option(label="English")
            time.sleep(0.5)
        if page.locator("select[name='1264-5-0']").count() > 0:
            page.locator("select[name='1264-5-0']").select_option(label="Fluent")
            time.sleep(0.5)
            
        # Consent checkbox (1266)
        cb = page.locator("input[name='1266']")
        if cb.count() > 0:
            cb.check(force=True)
            time.sleep(0.5)
            
        # Smooth scroll down
        for f in [0.3, 0.6, 0.9, 1.0]:
            page.evaluate(f"window.scrollTo(0, document.body.scrollHeight * {f})")
            time.sleep(0.5)
            
        # Look for the Step 2 submit / continue button
        print("Finding Continue/Next button...")
        submit_btn = page.locator("button[type='submit'], input[type='submit'], button:has-text('Continue'), button:has-text('Next')")
        print(f"Submit buttons: {submit_btn.count()}")
        for i in range(submit_btn.count()):
            btn = submit_btn.nth(i)
            print(f"  Btn {i}: '{btn.inner_text().strip()}' visible={btn.is_visible()}")
            
        # Click the primary submit button to move to Step 3 (Review)
        primary_btn = page.locator("button.button--primary:visible, input.button--primary:visible, button:has-text('Continue'):visible")
        if primary_btn.count() > 0:
            print("Clicking Continue to Review step...")
            primary_btn.first.click()
            page.wait_for_timeout(6000)
            
        print("Current URL:", page.url)
        print("Current Title:", page.title())
        print("Current Body excerpt:", page.inner_text("body")[:600])
        
        # Take full review screenshot
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"Screenshot saved to: {screenshot_path}")
        print("\n>>> STAGED ON REVIEW / FORM COMPLETE: READY FOR HUMAN SUBMISSION <<<")
        print("Never clicking final submit per policy.")
        
        browser.close()

if __name__ == "__main__":
    stage_harman()
