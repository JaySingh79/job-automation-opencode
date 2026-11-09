import os
from playwright.sync_api import sync_playwright

def inspect_infor_and_harman():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36")
        
        # Infor
        print("=== INFOR FORM ===")
        page = ctx.new_page()
        try:
            page.goto("https://careers.infor.com/en/postings/0029cdab-7f9d-4a7c-b33a-c32a2fe77160/applications/new", wait_until="networkidle", timeout=25000)
            page.wait_for_timeout(2000)
            print("Infor Form URL:", page.url)
            print("Infor Title:", page.title())
            inputs = page.query_selector_all("input, select, textarea")
            print(f"Inputs count: {len(inputs)}")
            for inp in inputs:
                name = inp.get_attribute("name") or inp.get_attribute("id") or inp.get_attribute("placeholder")
                itype = inp.get_attribute("type")
                vis = inp.is_visible()
                req = inp.get_attribute("required") is not None or "required" in (inp.get_attribute("class") or "")
                print(f"  [{itype}] name='{name}' visible={vis} req={req}")
        except Exception as e:
            print("Infor error:", e)
        finally:
            page.close()
            
        # Harman
        print("\n=== HARMAN APPLICATION METHODS ===")
        page2 = ctx.new_page()
        try:
            page2.goto("https://jobsearch.harman.com/en_US/careers/ApplicationMethods?jobId=32726", wait_until="networkidle", timeout=25000)
            page2.wait_for_timeout(2000)
            print("Harman URL:", page2.url)
            print("Harman Title:", page2.title())
            links = page2.query_selector_all("a")
            for l in links:
                txt = l.inner_text().strip()
                href = l.get_attribute("href")
                if txt or "apply" in (href or "").lower():
                    print("  Link:", txt, "->", href)
        except Exception as e:
            print("Harman error:", e)
        finally:
            page2.close()
            
        browser.close()

if __name__ == "__main__":
    inspect_infor_and_harman()
