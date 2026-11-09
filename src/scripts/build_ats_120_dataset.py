"""
Dataset Builder & Live URL Verifier for 4-ATS Universal Filler Training & 120-Job Evaluation.
Collects unique Ashby, Greenhouse, Lever, and SmartRecruiters URLs from local search results
and SerpApi Google Search, verifies HTTP/page liveness, and splits them into strictly disjoint:
  - TRAIN set: >= 10 per platform (for iterative debugging & edge-case discovery)
  - TEST set:  30 completely unseen live URLs per platform (120 total) for final evaluation
"""

import concurrent.futures
import glob
import json
import os
import re
import subprocess
import sys
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(r"D:\Projects\PRACTICE\firecrawl_test")
SEARCH_DIR = ROOT / "src" / "job_search_results"
OUT_DATASET = SEARCH_DIR / "ats_120_eval_dataset.json"


def normalize_url(url: str):
    if not url or not isinstance(url, str):
        return None, None
    url = url.strip()
    # Strip query params and trailing slashes for canonical deduping
    # Ashby: https://jobs.ashbyhq.com/<org>/<uuid>
    m_ashby = re.match(r"(https?://jobs\.ashbyhq\.com/[^/?#]+/[0-9a-fA-F-]{30,36})", url)
    if m_ashby:
        return "ashby", m_ashby.group(1)

    # Greenhouse: https://job-boards.greenhouse.io/<org>/jobs/<id> or boards.greenhouse.io/<org>/jobs/<id>
    m_gh = re.match(r"(https?://(?:job-boards|boards)\.greenhouse\.io/[^/?#]+/jobs/\d+)", url)
    if m_gh:
        return "greenhouse", m_gh.group(1)

    # Lever: https://jobs.lever.co/<org>/<uuid>
    m_lever = re.match(r"(https?://jobs\.lever\.co/[^/?#]+/[0-9a-fA-F-]{30,36})", url)
    if m_lever:
        return "lever", m_lever.group(1)

    # SmartRecruiters: https://jobs.smartrecruiters.com/<Company>/<id...>
    m_sr = re.match(r"(https?://jobs\.smartrecruiters\.com/[^/?#]+/\d{8,}[^/?#]*)", url)
    if m_sr:
        return "smartrecruiters", m_sr.group(1)

    return None, None


def harvest_local_urls():
    pools = {"ashby": set(), "greenhouse": set(), "lever": set(), "smartrecruiters": set()}
    for path in SEARCH_DIR.glob("*.json"):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
            # Extract all URLs via regex
            raw_urls = re.findall(r"https?://[^\s\"'<>\\]+", text)
            for u in raw_urls:
                ats, norm = normalize_url(u)
                if ats and norm:
                    pools[ats].add(norm)
        except Exception:
            pass
    return pools


def run_serpapi_queries(queries, ats_type, target_set):
    for q in queries:
        print(f"[SerpApi] Searching for {ats_type}: {q}")
        cmd = [
            "uv", "run", "--no-project", "python",
            str(ROOT / "src" / "scripts" / "serpapi_search.py"),
            "--query", q,
            "--num-pages", "2"
        ]
        try:
            res = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=60)
            if res.returncode == 0 and res.stdout:
                raw_urls = re.findall(r"https?://[^\s\"'<>\\]+", res.stdout)
                before = len(target_set)
                for u in raw_urls:
                    a, norm = normalize_url(u)
                    if a == ats_type and norm:
                        target_set.add(norm)
                print(f"  -> Added {len(target_set) - before} new {ats_type} URLs (total candidate pool: {len(target_set)})")
        except Exception as e:
            print(f"  -> SerpApi error: {e}")


def check_url_live(ats: str, url: str) -> tuple[str, str, bool, str]:
    """Fast HTTP check to filter out dead/404/redirected job postings."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "identity",
    }
    try:
        if ats == "ashby":
            # Verify via Ashby's public GraphQL endpoint so SPA shell 200s on closed jobs are filtered out!
            m = re.match(r"https?://jobs\.ashbyhq\.com/([^/?#]+)/([0-9a-fA-F-]{30,36})", url)
            if not m:
                return ats, url, False, "Bad Ashby URL"
            org, jid = m.group(1), m.group(2)
            gql_url = "https://jobs.ashbyhq.com/api/non-user-graphql?op=ApiJobPosting"
            payload = json.dumps({
                "operationName": "ApiJobPosting",
                "variables": {"organizationHostedJobsPageName": org, "jobPostingId": jid},
                "query": "query ApiJobPosting($organizationHostedJobsPageName: String!, $jobPostingId: String!) { jobPosting(organizationHostedJobsPageName: $organizationHostedJobsPageName, jobPostingId: $jobPostingId) { id title } }"
            }).encode("utf-8")
            req = urllib.request.Request(
                gql_url,
                data=payload,
                headers={**headers, "Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode("utf-8", errors="ignore"))
                jp = (data.get("data") or {}).get("jobPosting")
                if jp and jp.get("id"):
                    return ats, url, True, "OK"
                return ats, url, False, "Ashby GraphQL jobPosting=null"

        check_target = url
        if ats == "lever":
            check_target = url.rstrip("/") + "/apply"

        req = urllib.request.Request(check_target, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            final_url = resp.geturl()
            status = resp.getcode()
            body = resp.read().decode("utf-8", errors="ignore")
            if status != 200:
                return ats, url, False, f"HTTP {status}"
            if "error=true" in final_url:
                return ats, url, False, "Redirected to error=true"
            if ats == "greenhouse":
                if "greenhouse.io" not in final_url:
                    return ats, url, False, f"Redirected off greenhouse: {final_url}"
                if "The job you are looking for is no longer open" in body or "Page not found" in body:
                    return ats, url, False, "Closed job text"
                if "first_name" not in body and "application" not in body.lower():
                    return ats, url, False, "No application form"
            elif ats == "lever":
                if "This job does not exist" in body or "The job posting you're looking for might have closed" in body:
                    return ats, url, False, "Closed Lever posting"
                if "name=\"name\"" not in body and "application-form" not in body and "resume" not in body.lower():
                    return ats, url, False, "No Lever form found"
            elif ats == "smartrecruiters":
                if "This job is no longer available" in body or "Oops, this job is not available" in body:
                    return ats, url, False, "Closed SmartRecruiters job"
                # Check that it didn't redirect to generic company home without a job ID
                if not re.search(r"/\d{8,}", final_url) and "oneclick-ui" not in final_url:
                    return ats, url, False, f"Redirected away from job: {final_url}"
            return ats, url, True, "OK"
    except urllib.error.HTTPError as e:
        return ats, url, False, f"HTTPError {e.code}"
    except Exception as e:
        return ats, url, False, f"Err: {str(e)[:40]}"


def main():
    pools = harvest_local_urls()
    for k, v in pools.items():
        print(f"Initial local pool for {k}: {len(v)} unique URLs")

    # Top up pools via SerpApi if below 55 candidates
    if len(pools["ashby"]) < 55:
        run_serpapi_queries([
            'site:jobs.ashbyhq.com ("Software Engineer" OR "Machine Learning" OR "AI Engineer" OR "Backend" OR "Data")',
            'site:jobs.ashbyhq.com ("Full Stack" OR "Platform Engineer" OR "Developer" OR "Python")',
        ], "ashby", pools["ashby"])

    if len(pools["greenhouse"]) < 65:
        run_serpapi_queries([
            'site:job-boards.greenhouse.io ("Software Engineer" OR "Machine Learning" OR "Data Engineer" OR "Backend")',
            'site:job-boards.greenhouse.io ("AI Engineer" OR "Full Stack" OR "Python" OR "Developer")',
        ], "greenhouse", pools["greenhouse"])

    if len(pools["lever"]) < 65:
        run_serpapi_queries([
            'site:jobs.lever.co ("Software Engineer" OR "Machine Learning" OR "Data Engineer" OR "Backend")',
            'site:jobs.lever.co ("AI Engineer" OR "Full Stack" OR "Developer" OR "Python")',
            'site:jobs.lever.co ("Engineer" OR "Developer") "Apply"',
        ], "lever", pools["lever"])

    if len(pools["smartrecruiters"]) < 65:
        run_serpapi_queries([
            'site:jobs.smartrecruiters.com ("Software Engineer" OR "Data" OR "Machine Learning" OR "Developer")',
            'site:jobs.smartrecruiters.com ("AI" OR "Backend" OR "Full Stack" OR "Python" OR "Engineer")',
            'site:jobs.smartrecruiters.com ("Analyst" OR "Cloud" OR "DevOps" OR "QA Engineer")',
        ], "smartrecruiters", pools["smartrecruiters"])

    verified = {"ashby": [], "greenhouse": [], "lever": [], "smartrecruiters": []}

    for ats in ["ashby", "greenhouse", "lever", "smartrecruiters"]:
        candidates = sorted(list(pools[ats]))
        print(f"\nVerifying {len(candidates)} candidate URLs for {ats}...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=15) as ex:
            futs = [ex.submit(check_url_live, ats, u) for u in candidates]
            for f in concurrent.futures.as_completed(futs):
                a, u, is_live, msg = f.result()
                if is_live:
                    verified[a].append(u)
        print(f"Verified LIVE {ats} URLs: {len(verified[ats])}")

    # Check if any platform needs more live URLs to reach >= 40 (10 train + 30 test)
    extra_queries = {
        "ashby": [
            'site:jobs.ashbyhq.com "Engineer" "Remote"',
            'site:jobs.ashbyhq.com "Software" "India" OR "United States"',
        ],
        "greenhouse": [
            'site:job-boards.greenhouse.io "Engineer" "India" OR "Remote"',
            'site:job-boards.greenhouse.io "Software" "Python"',
        ],
        "lever": [
            'site:jobs.lever.co "Software" "Remote" OR "India" OR "USA"',
            'site:jobs.lever.co "Engineer" "Data" OR "Cloud" OR "Backend"',
        ],
        "smartrecruiters": [
            'site:jobs.smartrecruiters.com "Software" "India" OR "Remote" OR "USA"',
            'site:jobs.smartrecruiters.com "Engineer" "Technology"',
        ],
    }

    for ats in ["ashby", "greenhouse", "lever", "smartrecruiters"]:
        if len(verified[ats]) < 40:
            old_candidates = set(pools[ats])
            run_serpapi_queries(extra_queries[ats], ats, pools[ats])
            new_cands = sorted(list(pools[ats] - old_candidates))
            if new_cands:
                with concurrent.futures.ThreadPoolExecutor(max_workers=15) as ex:
                    futs = [ex.submit(check_url_live, ats, u) for u in new_cands]
                    for f in concurrent.futures.as_completed(futs):
                        a, u, is_live, msg = f.result()
                        if is_live and u not in verified[a]:
                            verified[a].append(u)
            print(f"Post-topup LIVE {ats} URLs: {len(verified[ats])}")

    dataset = {
        "created_at": "2026-10-20",
        "counts": {},
        "train": {},
        "test_30": {},
        "backup": {},
    }
    for ats in ["ashby", "greenhouse", "lever", "smartrecruiters"]:
        urls = verified[ats]
        # Reserve strictly 30 unseen URLs for test_30, 15 for train, and the rest in backup
        test_30 = urls[:30]
        train = urls[30:45] if len(urls) > 30 else urls[:10]
        backup = urls[45:] if len(urls) > 45 else []
        dataset["test_30"][ats] = test_30
        dataset["train"][ats] = train
        dataset["backup"][ats] = backup
        dataset["counts"][ats] = {
            "total_live": len(urls),
            "train_count": len(train),
            "test_30_count": len(test_30),
            "backup_count": len(backup),
        }

    OUT_DATASET.write_text(json.dumps(dataset, indent=2), encoding="utf-8")
    print("\nSaved dataset to:", OUT_DATASET)
    print(json.dumps(dataset["counts"], indent=2))


if __name__ == "__main__":
    main()
