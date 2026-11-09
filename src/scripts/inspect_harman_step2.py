import os
import time
from playwright.sync_api import sync_playwright

url = "https://jobsearch.harman.com/en_US/careers/ApplicationMethods?jobId=32726"
resume_path = r"D:\Projects\PRACTICE\firecrawl_test\Resumes\Jay Resume GenAI+DS 5th Aug.pdf"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36")
    page = ctx.new_page()
    page.goto(url, wait_until="domcontentloaded", timeout=20000)
    page.wait_for_timeout(2000)
    
    with page.expect_file_chooser() as fc_info:
        page.locator("#methodButton--file").click()
    file_chooser = fc_info.value
    file_chooser.set_files(resume_path)
    page.wait_for_timeout(3000)
    page.locator("#uploadFileResume").click()
    page.wait_for_timeout(5000)
    
    inputs = page.query_selector_all("input, select, textarea")
    print(f"Step 2 inputs ({len(inputs)}):")
    for inp in inputs:
        itype = inp.get_attribute("type")
        name = inp.get_attribute("name") or inp.get_attribute("id")
        vis = inp.is_visible()
        req = inp.get_attribute("required") is not None
        val = inp.get_attribute("value") or ""
        lbl = inp.evaluate("el => el.closest('.fieldSpec') ? el.closest('.fieldSpec').querySelector('label')?.innerText : ''")
        print(f"  [{itype}] name='{name}' vis={vis} req={req} val='{val}' label='{lbl}'")
        
    browser.close()
