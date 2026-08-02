import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = await context.new_page()
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        url = "https://gartner.wd5.myworkdayjobs.com/EXT/job/Gurgaon/Data-Scientist--Classical-ML--NLP---LLM-GenAI-Agentic-AI-_110911/apply?source=JB-10120"
        print(f"Navigating to: {url}")
        
        response = await page.goto(url, wait_until="networkidle", timeout=40000)
        print(f"Response Status: {response.status}")
        
        # Wait for workday root element or buttons
        try:
            await page.wait_for_selector("a[data-automation-id='autofillWithResume'], button, main", timeout=15000)
            print("Workday DOM Elements Loaded!")
        except Exception as e:
            print(f"Selector wait timeout: {e}")
            
        title = await page.title()
        print(f"Page Title: {title}")
        
        buttons = await page.eval_on_selector_all("a, button", "els => els.map(e => e.innerText.trim()).filter(Boolean)")
        print(f"Interactive elements found: {buttons[:10]}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
