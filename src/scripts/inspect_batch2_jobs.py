import json
import os
import sys
import re
from playwright.sync_api import sync_playwright

def inspect_jobs():
    json_path = os.path.join("src", "job_search_results", "naukri", "direct_company_platforms", "batch_phenom_radancy.json")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    results = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        for idx, job in enumerate(data['jobs']):
            jid = job['job_id']
            company = job['company']
            title = job['title']
            url = job['company_site_url']
            
            print(f"\n--- [{idx+1}/{len(data['jobs'])}] {company} - {title} ---")
            print(f"URL: {url}")
            
            info = {
                "index": idx + 1,
                "job_id": jid,
                "company": company,
                "title": title,
                "url": url,
                "status": "pending",
                "reason": ""
            }
            
            # Rule fast bailouts on title: Senior / Lead / Principal / Sr
            title_lower = title.lower()
            if any(term in title_lower for term in ["senior", "lead", "principal", "sr."]):
                info["status"] = "skipped"
                info["reason"] = f"Title contains senior/lead/principal: '{title}'"
                print(f"-> SKIPPED: {info['reason']}")
                results.append(info)
                continue
            
            try:
                response = page.goto(url, wait_until="domcontentloaded", timeout=20000)
                page.wait_for_timeout(2000)
                
                final_url = page.url
                page_title = page.title()
                body_text = page.inner_text("body")[:3000]
                
                # Check for closed/expired indicators
                closed_indicators = [
                    "this job is no longer available",
                    "position has been filled",
                    "job has expired",
                    "requisition is closed",
                    "job posting is closed",
                    "no longer accepting applications",
                    "404 not found",
                    "page not found",
                    "the job you are looking for is closed",
                    "job is closed"
                ]
                
                is_closed = any(ci in body_text.lower() for ci in closed_indicators)
                if response and response.status >= 400:
                    info["status"] = "skipped"
                    info["reason"] = f"HTTP {response.status}"
                    print(f"-> SKIPPED: HTTP {response.status}")
                elif is_closed:
                    info["status"] = "skipped"
                    info["reason"] = "Job posting is expired or closed"
                    print("-> SKIPPED: Job posting is expired or closed")
                else:
                    info["status"] = "active"
                    info["final_url"] = final_url
                    info["page_title"] = page_title
                    # Check apply button presence
                    apply_btn = page.query_selector("button:has-text('Apply'), a:has-text('Apply')")
                    info["has_apply"] = bool(apply_btn)
                    print(f"-> ACTIVE | Title: {page_title} | Apply button: {bool(apply_btn)}")
                    
            except Exception as e:
                info["status"] = "error"
                info["reason"] = str(e)
                print(f"-> ERROR: {e}")
                
            results.append(info)
            
        browser.close()
        
    out_path = os.path.join("src", "application_progress", "direct_corporate", "batch2_inspect_summary.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nInspection completed. Results saved to {out_path}")

if __name__ == "__main__":
    inspect_jobs()
