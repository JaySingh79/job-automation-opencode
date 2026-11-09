#!/usr/bin/env python3
"""Async Prospeo API client for bulk corporate email retrieval and enrichment.

Uses the 'prospeo' environment variable for the API key (falls back to PROSPEO_API_KEY).
Supports:
  - Account info & credit checks
  - Single & concurrent person enrichment (/enrich-person)
  - Native bulk person enrichment (/bulk-enrich-person, up to 50 leads/call)
  - Filtered person search (/search-person)
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from typing import Any, Dict, List, Optional
import httpx
from dotenv import load_dotenv

load_dotenv()


def get_api_key() -> str:
    """Retrieve API key from 'prospeo' or 'PROSPEO_API_KEY'."""
    key = os.getenv("prospeo") or os.getenv("PROSPEO_API_KEY")
    if not key:
        raise ValueError(
            "Missing Prospeo API key. Please set the 'prospeo' (or 'PROSPEO_API_KEY') environment variable."
        )
    return key.strip()


class AsyncProspeoClient:
    """Asynchronous client for interacting with Prospeo REST API."""

    BASE_URL = "https://api.prospeo.io"

    def __init__(
        self,
        api_key: Optional[str] = None,
        concurrency_limit: int = 5,
        timeout: float = 30.0,
    ):
        self.api_key = api_key or get_api_key()
        self.semaphore = asyncio.Semaphore(concurrency_limit)
        self.headers = {
            "Content-Type": "application/json",
            "X-KEY": self.api_key,
        }
        self.timeout = httpx.Timeout(timeout)
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> AsyncProspeoClient:
        self._client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers=self.headers,
            timeout=self.timeout,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.BASE_URL,
                headers=self.headers,
                timeout=self.timeout,
            )
        return self._client

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def get_account_info(self) -> Dict[str, Any]:
        """Check credit balance and plan limits."""
        async with self.semaphore:
            resp = await self.client.get("/account-information")
            resp.raise_for_status()
            return resp.json()

    async def enrich_person(
        self,
        full_name: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        company_domain: Optional[str] = None,
        company_name: Optional[str] = None,
        linkedin_url: Optional[str] = None,
        only_verified_email: bool = True,
        enrich_mobile: bool = False,
    ) -> Dict[str, Any]:
        """Enrich a single individual to get corporate email."""
        data_payload: Dict[str, Any] = {}
        if full_name:
            data_payload["full_name"] = full_name
        if first_name:
            data_payload["first_name"] = first_name
        if last_name:
            data_payload["last_name"] = last_name
        if company_domain:
            data_payload["company_website"] = company_domain
        if company_name:
            data_payload["company_name"] = company_name
        if linkedin_url:
            data_payload["linkedin_url"] = linkedin_url

        payload = {
            "only_verified_email": only_verified_email,
            "enrich_mobile": enrich_mobile,
            "data": data_payload,
        }

        async with self.semaphore:
            resp = await self.client.post("/enrich-person", json=payload)
            if resp.status_code in (400, 404):
                try:
                    err_json = resp.json()
                    if err_json.get("error_code") == "NO_MATCH":
                        return {"matched": False, "error_code": "NO_MATCH", "response": None}
                    return err_json
                except Exception:
                    return {"matched": False, "status_code": resp.status_code}
            resp.raise_for_status()
            return resp.json()

    async def bulk_enrich_persons(
        self,
        leads: List[Dict[str, Any]],
        only_verified_email: bool = True,
        enrich_mobile: bool = False,
    ) -> Dict[str, Any]:
        """Native bulk enrichment endpoint.

        Prospeo accepts up to 50 records per request.
        Each item in leads should be a dict with identifiers e.g.:
        {'first_name': '...', 'last_name': '...', 'company_website': '...'}
        """
        payload = {
            "only_verified_email": only_verified_email,
            "enrich_mobile": enrich_mobile,
            "data": leads,
        }
        async with self.semaphore:
            resp = await self.client.post("/bulk-enrich-person", json=payload)
            resp.raise_for_status()
            return resp.json()

    async def enrich_many_concurrently(
        self,
        leads: List[Dict[str, Any]],
        batch_size: int = 50,
        only_verified_email: bool = True,
    ) -> List[Dict[str, Any]]:
        """Chunk a list of leads into batches of 50 and process in parallel."""
        tasks = []
        for i in range(0, len(leads), batch_size):
            chunk = leads[i : i + batch_size]
            tasks.append(
                self.bulk_enrich_persons(
                    chunk, only_verified_email=only_verified_email
                )
            )

        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        results = []
        for idx, res in enumerate(batch_results):
            if isinstance(res, Exception):
                results.append({"batch_index": idx, "error": str(res)})
            else:
                results.append(res)
        return results

    async def search_persons(
        self,
        company_domains: Optional[List[str]] = None,
        job_titles: Optional[List[str]] = None,
        locations: Optional[List[str]] = None,
        page: int = 1,
    ) -> Dict[str, Any]:
        """Search the Prospeo contact database by domain/title/location."""
        filters: Dict[str, Any] = {}
        if company_domains:
            filters["company_websites"] = company_domains
        if job_titles:
            filters["job_titles"] = job_titles
        if locations:
            filters["locations"] = locations

        payload = {"filters": filters, "page": page}
        async with self.semaphore:
            resp = await self.client.post("/search-person", json=payload)
            resp.raise_for_status()
            return resp.json()


async def demo():
    """Demo usage showing how to call the async client."""
    print("[*] Initializing Async Prospeo Client...")
    try:
        async with AsyncProspeoClient(concurrency_limit=5) as prospeo:
            # 1. Check account info
            info = await prospeo.get_account_info()
            print("[+] Account Info:", json.dumps(info, indent=2))

            # 2. Example: Single Enrichment
            lead = await prospeo.enrich_person(
                full_name="Sundar Pichai",
                company_domain="google.com",
            )
            print("[+] Enriched Person:", json.dumps(lead, indent=2))

            # 3. Example: Bulk Enrichment (up to 50 per batch)
            sample_leads = [
                {"full_name": "Satya Nadella", "company_website": "microsoft.com"},
                {"full_name": "Tim Cook", "company_website": "apple.com"},
            ]
            bulk_res = await prospeo.bulk_enrich_persons(sample_leads)
            print("[+] Bulk Enrichment Result:", json.dumps(bulk_res, indent=2))

    except ValueError as e:
        print(f"[-] Configuration Error: {e}", file=sys.stderr)
    except httpx.HTTPStatusError as e:
        print(f"[-] HTTP Error {e.response.status_code}: {e.response.text}", file=sys.stderr)
    except Exception as e:
        print(f"[-] Error: {e}", file=sys.stderr)


if __name__ == "__main__":
    asyncio.run(demo())
