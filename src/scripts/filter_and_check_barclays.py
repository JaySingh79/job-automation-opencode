import json
import re
from playwright.sync_api import sync_playwright

barclays_jobs = [
    {
        "id": "050826503403",
        "title": "Data Engineer ETL",
        "site_url": "https://search.jobs.barclays/job/chennai/data-engineer-etl/13015/98706401312"
    },
    {
        "id": "060826500169",
        "title": "Software Engineer",
        "site_url": "https://search.jobs.barclays/job/pune/software-engineer/13015/98800934752"
    },
    {
        "id": "211026501701",
        "title": "Customer Journey Labs Software Engineer - BA4",
        "site_url": "https://search.jobs.barclays/job/bengaluru/customer-journey-labs-software-engineer-ba4/13015/102153033616"
    },
    {
        "id": "271026501232",
        "title": "Software Engineer",
        "site_url": "https://search.jobs.barclays/job/pune/software-engineer/13015/102470599392"
    },
    {
        "id": "271026501222",
        "title": "Devops Engineer",
        "site_url": "https://search.jobs.barclays/job/pune/devops-engineer/13015/102470599664"
    },
    {
        "id": "040926501623",
        "title": "DevOps Engineer",
        "site_url": "https://search.jobs.barclays/job/pune/devops-engineer/13015/100080978368"
    }
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36")
    
    for job in barclays_jobs:
        print(f"\n==========================================")
        print(f"Barclays Job: {job['title']} ({job['id']})")
        print(f"Site URL: {job['site_url']}")
        page = ctx.new_page()
        try:
            page.goto(job['site_url'], wait_until="domcontentloaded", timeout=20000)
            page.wait_for_timeout(2000)
            
            # Find workday apply link
            wd_link = page.query_selector("a[href*='myworkdayjobs.com']")
            wd_url = wd_link.get_attribute("href") if wd_link else None
            print("Workday URL:", wd_url)
            
            # Get text from page
            body = page.inner_text("body")
            
            # Check for expectations/level
            levels = re.findall(r'(Assistant Vice President|Vice President|AVP|VP|BA3|BA4|Analyst)', body)
            print("Detected levels:", set(levels))
            
            # Check python vs java
            has_python = bool(re.search(r'\bpython\b', body, re.I))
            has_java = bool(re.search(r'\bjava\b', body, re.I))
            print(f"Skills: Python={has_python}, Java={has_java}")
            
            # Check experience mentions
            exps = re.findall(r'(\d+[\+\-\s]*(?:to\s*\d+)?\s*(?:years?|yrs?)(?:\s+of)?\s+experience)', body, re.I)
            print("Experience mentions:", exps[:4])
            
        except Exception as e:
            print("Error:", e)
        finally:
            page.close()
            
    browser.close()
