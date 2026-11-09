import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    
    # 1. Flymedia
    print("--- Inspecting Flymedia /apply-for-job/ ---")
    page1 = browser.new_page()
    page1.goto("https://flymediatech.com/apply-for-job/", wait_until="domcontentloaded", timeout=20000)
    time.sleep(2)
    print("Flymedia title:", page1.title())
    inputs1 = page1.locator("input:visible, textarea:visible, select:visible")
    print("Visible inputs count:", inputs1.count())
    for i in range(inputs1.count()):
        inp = inputs1.nth(i)
        print(f" [{i}] {inp.evaluate('el => el.tagName')} name={inp.get_attribute('name')} id={inp.get_attribute('id')} type={inp.get_attribute('type')} placeholder={inp.get_attribute('placeholder')}")
    page1.close()
    
    # 2. Tesco
    print("\n--- Inspecting Tesco ApplicationMethods ---")
    page2 = browser.new_page()
    page2.goto("https://careers.tesco.com/en_GB/careers/ApplicationMethods?jobId=140615", wait_until="domcontentloaded", timeout=20000)
    time.sleep(2)
    print("Tesco title:", page2.title())
    print("Tesco current URL:", page2.url)
    inputs2 = page2.locator("input:visible, textarea:visible, select:visible, a:visible, button:visible")
    print("Visible interactive elements:", inputs2.count())
    for i in range(min(inputs2.count(), 15)):
        el = inputs2.nth(i)
        print(f" [{i}] {el.evaluate('el => el.tagName')} text={el.inner_text().strip()[:30]} href={el.get_attribute('href')}")
    page2.close()
    
    browser.close()
