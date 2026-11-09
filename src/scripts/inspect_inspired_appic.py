import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    
    # 1. Inspired Infotech
    page1 = browser.new_page()
    page1.goto("https://inspiredinfotech.com/jobs/associate-ai-engineer-fresher-hyderabad.html", wait_until="domcontentloaded", timeout=20000)
    time.sleep(2)
    print("Inspired Infotech title:", page1.title())
    inps1 = page1.locator("input:visible, textarea:visible, select:visible, a:has-text('Apply'), button:has-text('Apply')")
    print("Inspired Infotech elements:")
    for i in range(inps1.count()):
        el = inps1.nth(i)
        print(f" [{i}] {el.evaluate('el => el.tagName')} text={el.inner_text().strip()[:30]} href={el.get_attribute('href')}")
    page1.close()
    
    # 2. Appic Softwares
    page2 = browser.new_page()
    page2.goto("https://appicsoftwares.com/careers/", wait_until="domcontentloaded", timeout=20000)
    time.sleep(2)
    print("\nAppic Softwares title:", page2.title())
    inps2 = page2.locator("input:visible, textarea:visible, select:visible")
    print("Appic inputs:")
    for i in range(inps2.count()):
        el = inps2.nth(i)
        print(f" [{i}] {el.evaluate('el => el.tagName')} name={el.get_attribute('name')} id={el.get_attribute('id')} placeholder={el.get_attribute('placeholder')}")
    page2.close()
    
    browser.close()
