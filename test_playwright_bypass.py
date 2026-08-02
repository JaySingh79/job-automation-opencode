import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox"
            ]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = await context.new_page()
        
        # Override navigator.webdriver
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        url = "https://www.linkedin.com/in/jay-singh-ds/details/experience/"
        print(f"Navigating to: {url}")
        
        try:
            response = await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            status = response.status if response else "No response"
            print(f"Response Status: {status}")
            
            await page.wait_for_timeout(3000)
            
            title = await page.title()
            print(f"Page Title: {title}")
            
            content = await page.content()
            print(f"Page Content Length: {len(content)} characters")
            
            if "Access Denied" in content or "Cloudflare" in content or "Captcha" in content or "Security Check" in content:
                print("RESULT: Anti-bot protection BLOCKED the request.")
            else:
                print("RESULT: SUCCESS - Bypassed anti-bot protection!")
                text = await page.inner_text("body")
                print("Snippet:\n" + text[:600])
        except Exception as e:
            print(f"Execution Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
