#!/usr/bin/env python3
"""Enrich real Indian startup profiles from funded_startups_last_6_months_200cr.json using Prospeo."""

import asyncio
import json
import os
import sys
from pathlib import Path
import httpx
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8")
load_dotenv()

API_KEY = os.getenv("prospeo") or os.getenv("PROSPEO_API_KEY")
if not API_KEY:
    print("[-] Missing Prospeo API key in environment variable 'prospeo'", file=sys.stderr)
    sys.exit(1)

# Notable Indian startup executives from the 200cr+ funded startups dataset
TARGETS = [
    {
        "company": "Zepto",
        "name": "Aadit Palicha",
        "role": "Co-Founder & CEO",
        "linkedin_url": "https://www.linkedin.com/in/aadit-palicha",
    },
    {
        "company": "CRED",
        "name": "Kunal Shah",
        "role": "Founder",
        "linkedin_url": "https://www.linkedin.com/in/kunalshah1",
    },
    {
        "company": "Darwinbox",
        "name": "Chaitanya Peddi",
        "role": "Co-Founder",
        "linkedin_url": "https://www.linkedin.com/in/chaitanyapeddi",
    },
    {
        "company": "Ather Energy",
        "name": "Tarun Mehta",
        "role": "Co-Founder & CEO",
        "linkedin_url": "https://www.linkedin.com/in/tarunsmehta",
    },
    {
        "company": "Moneyview",
        "name": "Puneet Agarwal",
        "role": "Co-Founder & CEO",
        "linkedin_url": "https://www.linkedin.com/in/puneet-agarwal-0268b81",
    },
]


async def enrich_lead(client: httpx.AsyncClient, target: dict) -> dict:
    payload = {
        "only_verified_email": False,
        "data": {
            "linkedin_url": target["linkedin_url"]
        }
    }
    try:
        resp = await client.post("/enrich-person", json=payload)
        if resp.status_code == 200:
            data = resp.json()
            person = data.get("person") or {}
            company = data.get("company") or {}
            email_data = person.get("email") or {}
            return {
                "matched": True,
                "target_company": target["company"],
                "target_name": target["name"],
                "full_name": person.get("full_name") or target["name"],
                "headline": person.get("headline", ""),
                "corporate_email": email_data.get("email"),
                "email_status": email_data.get("status"),
                "verification_method": email_data.get("verification_method"),
                "company_name": company.get("name") or target["company"],
                "company_domain": company.get("domain"),
            }
        elif resp.status_code in (400, 404):
            return {
                "matched": False,
                "target_company": target["company"],
                "target_name": target["name"],
                "error": resp.json().get("error_code", "NO_MATCH"),
            }
        elif resp.status_code == 429:
            return {
                "matched": False,
                "target_company": target["company"],
                "target_name": target["name"],
                "error": "Rate limit reached (Free tier is 1 req/sec)",
            }
        else:
            return {
                "matched": False,
                "target_company": target["company"],
                "target_name": target["name"],
                "error": f"HTTP {resp.status_code}",
            }
    except Exception as e:
        return {
            "matched": False,
            "target_company": target["company"],
            "target_name": target["name"],
            "error": str(e),
        }


async def main():
    print(f"[*] Testing Prospeo on 5 Indian Funded Startups from dataset...\n")

    headers = {
        "X-KEY": API_KEY,
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(base_url="https://api.prospeo.io", headers=headers, timeout=30.0) as client:
        # Check Account Credits
        acc_resp = await client.get("/account-information")
        if acc_resp.status_code == 200:
            acc_data = acc_resp.json().get("response", {})
            print(f"[*] Account: Plan={acc_data.get('current_plan')} | Remaining Credits={acc_data.get('remaining_credits')}\n")

        results = []
        for target in TARGETS:
            print(f"---> Querying {target['name']} ({target['company']})...")
            res = await enrich_lead(client, target)
            if res.get("matched"):
                print(f"     [+] FOUND: {res['full_name']}")
                print(f"         Email: {res['corporate_email']} (Status: {res['email_status']})")
                print(f"         Method: {res['verification_method']}")
                print(f"         Domain: {res['company_domain']}")
            else:
                print(f"     [-] No match / Error: {res.get('error')}")
            results.append(res)
            # Sleep 1.2s to respect Free Tier 1 req/sec limit
            await asyncio.sleep(1.2)

        print("\n" + "=" * 70)
        print("SUMMARY TABLE:")
        print(f"{'Company':<15} | {'Executive':<18} | {'Corporate Email':<30} | {'Status'}")
        print("-" * 70)
        for r in results:
            email = r.get("corporate_email") or r.get("error", "N/A")
            status = r.get("email_status") or "-"
            print(f"{r['target_company']:<15} | {r['target_name']:<18} | {email:<30} | {status}")
        print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
