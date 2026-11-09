#!/usr/bin/env python3
"""Antigravity Python CLI port of .opencode/tools/google_search.ts.

Executes paginated Google searches via SerpApi (up to 5 pages, 10 results/page),
deduplicates results by link, and returns JSON capped at 15,000 characters.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

MAX_CHARS = 15000
KEY_NAMES = ("SERPAPI_API_KEY", "SERP_API_KEY", "SERPAPI_KEY")


def _load_env_fallback() -> None:
    for k in KEY_NAMES:
        if os.environ.get(k):
            return

    cur = Path.cwd().resolve()
    for _ in range(6):
        env_path = cur / ".env"
        if env_path.is_file():
            try:
                for line in env_path.read_text(encoding="utf-8").splitlines():
                    trimmed = line.strip()
                    if not trimmed or trimmed.startswith("#"):
                        continue
                    m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$", trimmed)
                    if not m:
                        continue
                    key, raw = m.group(1), m.group(2).strip()
                    if key not in KEY_NAMES or os.environ.get(key):
                        continue
                    if (
                        len(raw) >= 2
                        and ((raw[0] == '"' and raw[-1] == '"') or (raw[0] == "'" and raw[-1] == "'"))
                    ):
                        raw = raw[1:-1]
                    if raw:
                        os.environ[key] = raw
            except Exception:
                pass
            return
        if cur.parent == cur:
            break
        cur = cur.parent


def _resolve_api_key() -> str | None:
    _load_env_fallback()
    for k in KEY_NAMES:
        val = os.environ.get(k)
        if val:
            return val
    return None


def run_search(
    query: str,
    num_pages: int = 5,
    gl: str = "us",
    hl: str = "en",
    google_domain: str = "google.com",
) -> str:
    api_key = _resolve_api_key()
    if not api_key:
        return "Error: SERPAPI_API_KEY (or SERP_API_KEY) not set in env/.env"

    num_pages = max(1, min(5, num_pages))
    collected: list[dict[str, str]] = []

    for page in range(num_pages):
        params = urllib.parse.urlencode(
            {
                "engine": "google",
                "q": query,
                "google_domain": google_domain,
                "hl": hl,
                "gl": gl,
                "start": page * 10,
                "api_key": api_key,
            }
        )
        url = f"https://serpapi.com/search.json?{params}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Antigravity-SerpApi/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = json.loads(resp.read().decode("utf-8", errors="replace"))
        except urllib.error.HTTPError as exc:
            err_text = exc.read().decode("utf-8", errors="replace") if exc.fp else str(exc)
            if collected:
                break
            return f"Error: SerpApi HTTP {exc.code} — {err_text}"
        except Exception as exc:
            msg = f"{type(exc).__name__}: {exc}"
            if not collected:
                return f"Error: SerpApi request failed — {msg}"
            break

        if isinstance(body, dict) and body.get("error"):
            if not collected:
                return f"Error: SerpApi returned an error — {body['error']}"
            break

        organic = body.get("organic_results") if isinstance(body, dict) else None
        if not organic:
            break

        for item in organic:
            if isinstance(item, dict):
                collected.append(
                    {
                        "title": str(item.get("title") or ""),
                        "link": str(item.get("link") or ""),
                        "snippet": str(item.get("snippet") or ""),
                    }
                )

    if not collected:
        return json.dumps(
            {"response": [], "note": "No organic_results returned for this query."},
            indent=2,
        )

    seen: set[str] = set()
    deduped: list[dict[str, str]] = []
    for item in collected:
        link = item.get("link", "")
        if link and link in seen:
            continue
        if link:
            seen.add(link)
        deduped.append(item)

    # Prune items from the end to stay under MAX_CHARS while maintaining valid JSON
    while deduped:
        rendered = json.dumps({"response": deduped}, indent=2)
        if len(rendered) <= MAX_CHARS or len(deduped) <= 1:
            return rendered
        deduped.pop()

    return json.dumps({"response": []}, indent=2)


def run_search_items(
    query: str,
    num_pages: int = 5,
    gl: str = "us",
    hl: str = "en",
    google_domain: str = "google.com",
) -> list[dict[str, str]]:
    api_key = _resolve_api_key()
    if not api_key:
        return []

    num_pages = max(1, min(5, num_pages))
    collected: list[dict[str, str]] = []
    seen: set[str] = set()

    for page in range(num_pages):
        params = urllib.parse.urlencode(
            {
                "engine": "google",
                "q": query,
                "google_domain": google_domain,
                "hl": hl,
                "gl": gl,
                "start": page * 10,
                "api_key": api_key,
            }
        )
        url = f"https://serpapi.com/search.json?{params}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Antigravity-SerpApi/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = json.loads(resp.read().decode("utf-8", errors="replace"))
        except Exception:
            break

        if isinstance(body, dict) and body.get("error"):
            break

        organic = body.get("organic_results") if isinstance(body, dict) else None
        if not organic:
            break

        for item in organic:
            if isinstance(item, dict):
                link = str(item.get("link") or "")
                if link and link not in seen:
                    seen.add(link)
                    collected.append(
                        {
                            "title": str(item.get("title") or ""),
                            "link": link,
                            "snippet": str(item.get("snippet") or ""),
                        }
                    )

    return collected


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Google search via SerpApi (mirrors .opencode/tools/google_search.ts)."
    )
    parser.add_argument("query_pos", nargs="?", help="Google search query string")
    parser.add_argument("-q", "--query", help="Google search query string")
    parser.add_argument(
        "-n",
        "--num-pages",
        type=int,
        default=5,
        help="Pages to fetch (10 results each, 1-5, default: 5)",
    )
    parser.add_argument("--gl", default="us", help="Geolocation (default: 'us')")
    parser.add_argument("--hl", default="en", help="Host language (default: 'en')")
    parser.add_argument(
        "--google-domain", default="google.com", help="Google domain (default: 'google.com')"
    )
    args = parser.parse_args()

    query = args.query or args.query_pos
    if not query:
        parser.error("A search query is required (pass positionally or via --query).")

    sys.stdout.reconfigure(encoding="utf-8")
    print(
        run_search(
            query=query,
            num_pages=args.num_pages,
            gl=args.gl,
            hl=args.hl,
            google_domain=args.google_domain,
        )
    )


if __name__ == "__main__":
    main()
