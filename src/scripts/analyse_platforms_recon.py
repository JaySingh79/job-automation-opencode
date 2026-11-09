"""
Platform Recon Analyzer
Analyzes DOM type, JS framework, event system, and navigation smoothness
across 3 jobs per target job board.
"""

import os
import sys
import json
import time
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

OUTPUT_FILE = "src/knowledge_source/ats_platforms_recon_analysis.json"

PLATFORMS_TO_TEST = [
    "workday",
    "oracle_cloud",
    "greenhouse",
    "smartrecruiters",
    "keka",
    "zoho_recruit",
    "darwinbox",
    "intellohire",
    "custom_company_careers"
]

def analyze_url(page, url):
    start_t = time.time()
    result = {
        "url": url,
        "load_time_ms": 0,
        "http_status": None,
        "frameworks": [],
        "dom_features": {},
        "security_anti_bot": [],
        "apply_flow_type": "unknown",
        "smoothness_score": "good"
    }

    try:
        resp = page.goto(url, timeout=30000, wait_until="domcontentloaded")
        result["load_time_ms"] = int((time.time() - start_t) * 1000)
        if resp:
            result["http_status"] = resp.status

        time.sleep(2)  # Allow JS hydration

        telemetry = page.evaluate("""() => {
            const fw = [];
            if (window.React || document.querySelector('[data-reactroot], [data-reactid], [data-react-helmet]')) fw.push('React');
            if (window.angular || document.querySelector('[ng-app], [ng-version], [_ngcontent]')) fw.push('Angular');
            if (window.Vue || document.querySelector('[data-v-]')) fw.push('Vue');
            if (window.__NEXT_DATA__) fw.push('Next.js');
            if (window.__NUXT__) fw.push('Nuxt');
            if (window.jQuery) fw.push('jQuery');
            if (window.OJ || window.oj) fw.push('Oracle JET');

            // Anti-bot
            const sec = [];
            if (window.grecaptcha || document.querySelector('.g-recaptcha, iframe[src*="recaptcha"]')) sec.push('Google reCAPTCHA');
            if (window.hcaptcha || document.querySelector('.h-captcha, iframe[src*="hcaptcha"]')) sec.push('hCaptcha');
            if (document.cookie.includes('cf_clearance') || document.querySelector('#challenge-running')) sec.push('Cloudflare');
            if (document.cookie.includes('bm_sz') || document.cookie.includes('ak_bmsc')) sec.push('Akamai');

            // DOM checks
            const iframesCount = document.querySelectorAll('iframe').length;
            const shadowRoots = Array.from(document.querySelectorAll('*')).filter(el => !!el.shadowRoot).length;
            const formCount = document.querySelectorAll('form').length;
            const applyButtons = Array.from(document.querySelectorAll('button, a')).filter(el => {
                const t = (el.innerText || '').toLowerCase();
                return t.includes('apply') || t.includes('submit') || t.includes('start application');
            }).map(b => b.innerText.trim().slice(0, 40)).slice(0, 3);

            const hasWizard = !!document.querySelector('.wizard, [role="progressbar"], .stepper, [class*="step"]');
            const hasAuthWall = /sign in|create account|log in to apply/i.test(document.body.innerText);

            return {
                fw,
                sec,
                iframesCount,
                shadowRoots,
                formCount,
                applyButtons,
                hasWizard,
                hasAuthWall,
                title: document.title
            };
        }""")

        result["frameworks"] = telemetry.get("fw", [])
        result["security_anti_bot"] = telemetry.get("sec", [])
        result["dom_features"] = {
            "title": telemetry.get("title"),
            "iframes": telemetry.get("iframesCount"),
            "shadow_roots": telemetry.get("shadowRoots"),
            "forms": telemetry.get("formCount"),
            "apply_buttons": telemetry.get("applyButtons")
        }

        if telemetry.get("hasAuthWall"):
            result["apply_flow_type"] = "auth_wall_required"
        elif telemetry.get("hasWizard"):
            result["apply_flow_type"] = "multi_step_wizard"
        elif telemetry.get("formCount") > 0:
            result["apply_flow_type"] = "single_page_form"
        else:
            result["apply_flow_type"] = "landing_redirect"

        if result["load_time_ms"] > 8000:
            result["smoothness_score"] = "heavy_sluggish"
        elif result["load_time_ms"] > 3500:
            result["smoothness_score"] = "moderate"
        else:
            result["smoothness_score"] = "fast_responsive"

    except Exception as e:
        result["error"] = str(e)[:150]
        result["smoothness_score"] = "timeout_or_error"

    return result

def run_recon():
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "platforms": {}
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768}
        )
        page = context.new_page()

        for plat in PLATFORMS_TO_TEST:
            plat_file = f"src/job_search_results/naukri/direct_company_platforms/{plat}.json"
            if not os.path.exists(plat_file):
                continue

            with open(plat_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            jobs = data.get("jobs", [])[:3]
            print(f"\n[Recon] Testing Platform: {plat} ({len(jobs)} sample jobs)...")

            plat_results = []
            for j in jobs:
                url = j.get("company_site_url")
                company = j.get("company")
                title = j.get("title")
                print(f"  -> Testing [{company}] {title} ...")
                res = analyze_url(page, url)
                res["company"] = company
                res["title"] = title
                plat_results.append(res)
                print(f"     Status: {res.get('http_status')} | Frameworks: {res.get('frameworks')} | Flow: {res.get('apply_flow_type')} | Speed: {res.get('smoothness_score')} ({res.get('load_time_ms')}ms)")

            report["platforms"][plat] = {
                "total_jobs_in_partition": data.get("total_jobs"),
                "samples_tested": plat_results
            }

        browser.close()

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        json.dump(report, out, indent=2)

    print(f"\nRecon analysis saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    run_recon()
