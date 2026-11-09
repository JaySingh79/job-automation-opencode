import os
import time
from playwright.sync_api import sync_playwright

def test_harman_upload():
    url = "https://jobsearch.harman.com/en_US/careers/ApplicationMethods?jobId=32726"
    resume_path = r"D:\Projects\PRACTICE\firecrawl_test\Resumes\Jay Resume GenAI+DS 5th Aug.pdf"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36")
        page = ctx.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=20000)
        page.wait_for_timeout(2000)
        
        print("Clicking file trigger with expect_file_chooser...")
        with page.expect_file_chooser() as fc_info:
            page.locator("#methodButton--file").click()
        file_chooser = fc_info.value
        file_chooser.set_files(resume_path)
        print("Resume set via file chooser!")
        page.wait_for_timeout(3000)
        
        btn = page.locator("#uploadFileResume")
        print("Continue button visible:", btn.is_visible())
        if btn.is_visible():
            btn.click()
            page.wait_for_timeout(5000)
            print("Post-click URL:", page.url)
            print("Post-click Title:", page.title())
            print("Post-click Body excerpt:", page.inner_text("body")[:800])
        browser.close()

if __name__ == "__main__":
    test_harman_upload()
