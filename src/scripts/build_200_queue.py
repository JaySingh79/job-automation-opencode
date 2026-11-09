"""
Build curated 200 Target + 30 Backup job queue for Ashby, Lever, and Greenhouse.
Saved to: src/job_search_results/ashby_lever_greenhouse/2026-11-06-fresh-200-queue.json
"""

import json
from pathlib import Path

ROOT = Path(r"D:\Projects\PRACTICE\firecrawl_test")
DIR_PATH = ROOT / "src" / "job_search_results" / "ashby_lever_greenhouse"
PROG_DIR = ROOT / "src" / "application_progress" / "ashby_lever_greenhouse"
APPLIED_DIR = ROOT / "src" / "applied"

def collect_applied_urls() -> set[str]:
    applied = set()
    for pf in list(PROG_DIR.glob("*.json*")) + list(APPLIED_DIR.glob("*.json*")):
        try:
            if pf.suffix == ".jsonl":
                for line in pf.read_text(encoding="utf-8").splitlines():
                    if line.strip():
                        data = json.loads(line)
                        if "url" in data and isinstance(data["url"], str):
                            applied.add(data["url"].strip().rstrip("/"))
            elif pf.suffix == ".json":
                data = json.loads(pf.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and "url" in item and isinstance(item["url"], str):
                            applied.add(item["url"].strip().rstrip("/"))
                elif isinstance(data, dict):
                    for k in ["passed_120", "results", "applied"]:
                        if k in data and isinstance(data[k], list):
                            for item in data[k]:
                                if isinstance(item, dict) and "url" in item and isinstance(item["url"], str):
                                    applied.add(item["url"].strip().rstrip("/"))
        except Exception:
            pass
    return applied

def build_queue():
    applied_urls = collect_applied_urls()
    print(f"Collected {len(applied_urls)} previously applied or attempted URLs.")

    priority_files = [
        "2026-10-18-fresh-100-ashby-lever-greenhouse.json",
        "2026-10-17-fresh-100-final.json",
        "2026-10-17-harvest-pool-2.json",
        "2026-10-17-harvest-pool.json",
        "ats_120_eval_dataset.json",
        "2026-10-13-ashby-lever-greenhouse-3yr-india-remote.json",
        "2026-10-04-fresher-50-india-remote.json",
    ]

    by_ats: dict[str, list[dict]] = {"ashby": [], "lever": [], "greenhouse": []}
    seen: set[str] = set()

    for fn in priority_files:
        fp = DIR_PATH / fn
        if not fp.exists():
            continue
        try:
            data = json.loads(fp.read_text(encoding="utf-8"))
            items = []
            if isinstance(data, list):
                items = data
            elif isinstance(data, dict):
                if "train" in data or "test_30" in data or "backup" in data:
                    for split in ["train", "test_30", "backup"]:
                        for ats, ulist in data.get(split, {}).items():
                            for u in ulist:
                                items.append({"url": u, "ats": ats, "title": "Software / AI Engineer", "source_file": fn})
                else:
                    for k, v in data.items():
                        if isinstance(v, list):
                            for x in v:
                                if isinstance(x, dict):
                                    items.append(x)
                                elif isinstance(x, str) and x.startswith("http"):
                                    items.append({"url": x, "source_file": fn})
            for item in items:
                url = item.get("url") or item.get("job_url") or item.get("link")
                if not url or not isinstance(url, str) or not url.startswith("http"):
                    continue
                clean_url = url.strip().rstrip("/")
                if clean_url in seen or clean_url in applied_urls:
                    continue

                ats = item.get("ats", "")
                if not ats:
                    if "ashby" in clean_url:
                        ats = "ashby"
                    elif "lever" in clean_url:
                        ats = "lever"
                    elif "greenhouse" in clean_url:
                        ats = "greenhouse"
                    else:
                        continue

                if ats not in by_ats:
                    continue

                title = (item.get("title") or item.get("role") or "").lower()
                if any(sr in title for sr in ["senior", "sr.", "principal", "staff", "lead", "director", "vp", "manager", "head"]):
                    continue

                seen.add(clean_url)
                by_ats[ats].append({
                    "ats": ats,
                    "url": clean_url,
                    "title": item.get("title") or item.get("role") or "Software / AI Engineer",
                    "company": item.get("company") or "",
                    "location": item.get("location") or "India / Remote",
                    "source": fn,
                })
        except Exception as e:
            print(f"Error reading {fn}: {e}")

    print(f"Candidate counts: Ashby={len(by_ats['ashby'])}, Lever={len(by_ats['lever'])}, Greenhouse={len(by_ats['greenhouse'])}")

    gh_pool = by_ats["greenhouse"]
    ashby_pool = by_ats["ashby"]
    lever_pool = by_ats["lever"]

    # Target: 200 jobs + 30 backup jobs = 230 total
    # Balanced distribution: 40 Greenhouse, 95 Ashby, 95 Lever
    selected_gh = gh_pool[:40]
    selected_ashby = ashby_pool[:95]
    selected_lever = lever_pool[:95]

    combined = []
    max_len = max(len(selected_ashby), len(selected_lever), len(selected_gh))
    for i in range(max_len):
        if i < len(selected_ashby):
            combined.append(selected_ashby[i])
        if i < len(selected_lever):
            combined.append(selected_lever[i])
        if i < len(selected_gh):
            combined.append(selected_gh[i])

    target_jobs = combined[:200]
    backup_jobs = combined[200:230]

    out_queue = {
        "metadata": {
            "date": "2026-11-06",
            "target_count": len(target_jobs),
            "backup_count": len(backup_jobs),
            "ats_breakdown_target": {
                "ashby": sum(1 for j in target_jobs if j["ats"] == "ashby"),
                "lever": sum(1 for j in target_jobs if j["ats"] == "lever"),
                "greenhouse": sum(1 for j in target_jobs if j["ats"] == "greenhouse"),
            },
            "ats_breakdown_backup": {
                "ashby": sum(1 for j in backup_jobs if j["ats"] == "ashby"),
                "lever": sum(1 for j in backup_jobs if j["ats"] == "lever"),
                "greenhouse": sum(1 for j in backup_jobs if j["ats"] == "greenhouse"),
            },
        },
        "target": target_jobs,
        "backup": backup_jobs,
    }

    out_path = DIR_PATH / "2026-11-06-fresh-200-queue.json"
    out_path.write_text(json.dumps(out_queue, indent=2), encoding="utf-8")
    print(f"Successfully wrote queue to {out_path}")
    print("Metadata:", json.dumps(out_queue["metadata"], indent=2))

if __name__ == "__main__":
    build_queue()
