import json
import os
import re
from playwright.sync_api import sync_playwright

def check_all():
    json_path = os.path.join("src", "job_search_results", "naukri", "direct_company_platforms", "batch_phenom_radancy.json")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    results = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(
            ignore_https_errors=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
        )
        
        for idx, job in enumerate(data['jobs']):
            jid = job['job_id']
            company = job['company']
            title = job['title']
            url = job['company_site_url']
            exp_naukri = job.get('experience', '')
            
            print(f"\n==========================================")
            print(f"[{idx+1}/{len(data['jobs'])}] {company} | {title} | Exp: {exp_naukri}")
            print(f"URL: {url}")
            
            item = {
                "index": idx + 1,
                "job_id": jid,
                "company": company,
                "title": title,
                "url": url,
                "naukri_exp": exp_naukri,
                "status": "pending",
                "notes": ""
            }
            
            # Fast title filter
            title_lower = title.lower()
            if any(term in title_lower for term in ["senior", "lead", "principal", "sr."]):
                item["status"] = "skipped"
                item["notes"] = f"Skipped by title rule (Senior/Lead/Principal): {title}"
                print(f"-> {item['notes']}")
                results.append(item)
                continue
                
            page = ctx.new_page()
            try:
                # 15s timeout
                res = page.goto(url, wait_until="domcontentloaded", timeout=18000)
                page.wait_for_timeout(2000)
                
                final_url = page.url
                page_title = page.title()
                body_text = page.inner_text("body")
                
                item["final_url"] = final_url
                item["page_title"] = page_title
                
                # Check closed / 404
                closed_phrases = [
                    "this job is no longer available",
                    "position has been filled",
                    "job has expired",
                    "requisition is closed",
                    "job posting is closed",
                    "no longer accepting applications",
                    "the job you are looking for is closed",
                    "job is closed",
                    "page not found",
                    "404 not found"
                ]
                
                if res and res.status >= 400:
                    item["status"] = "skipped"
                    item["notes"] = f"HTTP {res.status}"
                    print(f"-> {item['notes']}")
                elif any(cp in body_text.lower() for cp in closed_phrases):
                    item["status"] = "skipped"
                    item["notes"] = "Posting is closed / expired / no longer available"
                    print(f"-> {item['notes']}")
                else:
                    item["status"] = "active"
                    # Look for experience mentions in body
                    exp_matches = re.findall(r'(\d+[\+\-\s]*(?:to\s*\d+)?\s*(?:years?|yrs?)(?:\s+of)?\s+experience)', body_text, re.IGNORECASE)
                    item["exp_mentions"] = exp_matches[:5]
                    
                    # Look for apply button
                    apply_elements = page.query_selector_all("a:has-text('Apply'), button:has-text('Apply'), input[value*='Apply']")
                    item["apply_buttons_count"] = len(apply_elements)
                    print(f"-> ACTIVE! Title: {page_title} | Exp mentions: {exp_matches[:3]} | Apply buttons: {len(apply_elements)}")
                    
            except Exception as e:
                item["status"] = "error"
                item["notes"] = f"Timeout/Error: {str(e)[:150]}"
                print(f"-> ERROR: {item['notes']}")
            finally:
                page.close()
                
            results.append(item)
            
        browser.close()
        
    out_file = os.path.join("src", "application_progress", "direct_corporate", "batch2_detailed_status.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved detailed status to {out_file}")

if __name__ == "__main__":
    check_all()
