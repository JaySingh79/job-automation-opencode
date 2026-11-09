#!/usr/bin/env python3
"""Enrich real Indian startup founders/executives from funded_startups_last_6_months_200cr.json."""

import asyncio
import json
import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parents[2]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.scripts.prospeo_async_client import AsyncProspeoClient

# Real startup leaders from the funded list:
TARGETS = [
    {
        "company": "Zepto",
        "full_name": "Aadit Palicha",
        "company_website": "zeptonow.com",
        "title": "Co-Founder & CEO"
    },
    {
        "company": "CRED",
        "full_name": "Kunal Shah",
        "company_website": "cred.club",
        "title": "Founder"
    },
    {
        "company": "Darwinbox",
        "full_name": "Chaitanya Peddi",
        "company_website": "darwinbox.com",
        "title": "Co-Founder"
    },
    {
        "company": "Battery Smart",
        "full_name": "Pulkit Khurana",
        "company_website": "batterysmart.in",
        "title": "Co-Founder"
    }
]


async def main():
    print(f"[*] Testing Prospeo Enrichment on {len(TARGETS)} Funded Indian Startup Leaders...\n")
    
    async with AsyncProspeoClient(concurrency_limit=1) as client:
        # Check current balance
        account = await client.get_account_info()
        print(f"[*] Account Status: Plan={account['response']['current_plan']} | Remaining Credits={account['response']['remaining_credits']}\n")

        results = []
        for target in TARGETS:
            print(f"---> Looking up: {target['full_name']} @ {target['company']} ({target['company_website']})...")
            try:
                res = await client.enrich_person(
                    full_name=target["full_name"],
                    company_domain=target["company_website"],
                    company_name=target["company"],
                    only_verified_email=False, # include all matched work emails
                )
                
                # Check for rate limit or errors
                if res.get("error"):
                    print(f"     [!] API Error: {res}")
                elif not res.get("matched", True) or not res.get("response"):
                    print(f"     [-] No direct email match found in database.")
                else:
                    person = res.get("response", {})
                    email = person.get("email") or person.get("work_email") or "N/A"
                    status = person.get("email_status") or person.get("status")
                    print(f"     [+] MATCH FOUND!")
                    print(f"         - Name: {person.get('full_name', target['full_name'])}")
                    print(f"         - Email: {email} (Status: {status})")
                    print(f"         - Title: {person.get('job_title', target['title'])}")
                    results.append(person)
            except Exception as e:
                print(f"     [-] Error: {e}")

            # Sleep 1.5s between requests to stay strictly within Free Tier 1 req/sec limit
            await asyncio.sleep(1.5)

        print("\n" + "="*60)
        print(f"[*] Finished test. Successfully retrieved {len(results)}/{len(TARGETS)} corporate profiles.")
        print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
