import asyncio
import json
import os
import sys

# Ensure src/scripts is in python path
sys.path.insert(0, os.path.dirname(__file__))
from prospeo_async_client import AsyncProspeoClient

# Target candidates: 2 per company across 5 startups (CRED, Darwinbox, Ather Energy, Moneyview, Zepto)
CANDIDATES = [
    # 1. CRED
    {
        "company": "CRED",
        "name": "Atish Munje",
        "title": "Principal Data Scientist",
        "linkedin_url": "https://in.linkedin.com/in/atishmunje"
    },
    {
        "company": "CRED",
        "name": "Mohit Garg",
        "title": "Principal Data Platform Engineer",
        "linkedin_url": "https://in.linkedin.com/in/mohit-garg-2838a025"
    },
    # 2. Darwinbox
    {
        "company": "Darwinbox",
        "name": "Dishant Patel",
        "title": "Engineering Manager (ex-Principal)",
        "linkedin_url": "https://in.linkedin.com/in/dishant-patel"
    },
    {
        "company": "Darwinbox",
        "name": "Amit Rathod",
        "title": "Solution Engineering Manager (AI & Enterprise)",
        "linkedin_url": "https://in.linkedin.com/in/rathodamit"
    },
    # 3. Ather Energy
    {
        "company": "Ather Energy",
        "name": "Vinayak Moger",
        "title": "Technical Lead / Staff Engineer",
        "linkedin_url": "https://in.linkedin.com/in/vinayak-moger-2b91b6135"
    },
    {
        "company": "Ather Energy",
        "name": "Srikantan Prakash",
        "title": "Lead Data Engineer",
        "linkedin_url": "https://in.linkedin.com/in/srikantan-prakash-2536845a"
    },
    # 4. Moneyview
    {
        "company": "Moneyview",
        "name": "Shubham Priyadarshi",
        "title": "Engineering Manager (AI Innovations)",
        "linkedin_url": "https://in.linkedin.com/in/shubham-priyadarshi-3627b731"
    },
    {
        "company": "Moneyview",
        "name": "Saksham Gupta",
        "title": "Staff Engineer",
        "linkedin_url": "https://in.linkedin.com/in/guptasaksham93"
    },
    # 5. Zepto
    {
        "company": "Zepto",
        "name": "Rajendra Bera",
        "title": "Principal Engineer",
        "linkedin_url": "https://in.linkedin.com/in/rajendra-bera"
    },
    {
        "company": "Zepto",
        "name": "Kshitij Singh",
        "title": "Engineering Manager",
        "linkedin_url": "https://in.linkedin.com/in/ikshitijsingh"
    }
]

async def run_enrichment():
    client = AsyncProspeoClient()
    print("Checking initial Prospeo account credits...")
    acct = await client.get_account_info()
    plan_info = acct.get("response", {}).get("plan", {})
    print(f"Plan: {plan_info.get('name')}, Credits Remaining: {plan_info.get('credits_remaining')}")

    enriched_results = []

    print(f"\nBeginning enrichment of {len(CANDIDATES)} candidates (paced at 1.5s/req)...")
    for i, c in enumerate(CANDIDATES, 1):
        print(f"[{i}/{len(CANDIDATES)}] Enriching {c['name']} ({c['company']} - {c['title']})...")
        try:
            res = await client.enrich_person(
                linkedin_url=c["linkedin_url"],
                only_verified_email=False
            )
            response_data = res.get("response", {}) or {}
            email_info = response_data.get("email", {}) if isinstance(response_data, dict) else {}
            person_info = response_data.get("person", {}) if isinstance(response_data, dict) else {}

            email_val = email_info.get("email") if isinstance(email_info, dict) else None
            email_status = email_info.get("status") if isinstance(email_info, dict) else None
            job_title = person_info.get("title") if isinstance(person_info, dict) else c["title"]

            enriched_results.append({
                "company": c["company"],
                "name": c["name"],
                "target_title": c["title"],
                "profile_title": job_title,
                "linkedin_url": c["linkedin_url"],
                "email": email_val or "Not Disclosed / Unavailable",
                "email_status": email_status or res.get("error_code") or "NO_MATCH",
                "full_response": res
            })
            print(f"   -> Result: email={email_val}, status={email_status}")
        except Exception as e:
            print(f"   -> Error: {e}")
            enriched_results.append({
                "company": c["company"],
                "name": c["name"],
                "target_title": c["title"],
                "linkedin_url": c["linkedin_url"],
                "email": "Error",
                "email_status": str(e),
                "full_response": {}
            })
        
        # Pacing to avoid 429 rate limit
        await asyncio.sleep(1.5)

    await client.close()

    # Save results to src/job_search_results/enriched_10_ai_leaders.json
    out_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "job_search_results",
        "enriched_10_ai_leaders.json"
    )
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(enriched_results, f, indent=2)

    print(f"\nFinished enrichment! Results saved to {out_path}")

if __name__ == "__main__":
    asyncio.run(run_enrichment())
