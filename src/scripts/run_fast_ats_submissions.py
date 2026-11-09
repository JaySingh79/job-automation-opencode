#!/usr/bin/env python3
"""
Fast ATS Submissions Runner.
Executes batch submissions across Ashby, Lever, and Greenhouse using 4 concurrent
Patchright workers with full submit authority, anti-bot stealth emulation, and fast throughput.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime
import json
import os
import random
import sys
import threading
import time
from pathlib import Path
from typing import Any

ROOT = Path(r"D:\Projects\PRACTICE\firecrawl_test")
sys.path.insert(0, str(ROOT))

from src.scripts.universal_ats_filler import (
    process_single_job,
    CANDIDATE,
    PROGRESS_DIR,
    SNAP_DIR,
)

AUTH_PATH = ROOT / "src" / "submit_permisssions" / "ashby_greenhouse_lever_submit_authority.json"
DEFAULT_QUEUE = ROOT / "src" / "job_search_results" / "ashby_lever_greenhouse" / "2026-11-07-fresh-300-ashby-lever-greenhouse.json"
PROGRESS_JSON = PROGRESS_DIR / "ashby_lever_greenhouse" / "2026-11-07-fast-batch-progress.json"
AUDIT_JSONL = PROGRESS_DIR / "ashby_lever_greenhouse" / "2026-11-07-fast-submit-audit.jsonl"
APPLIED_ATS_PATH = ROOT / "src" / "applied" / "ashby_lever_greenhouse.json"
APPLIED_MASTER_PATH = ROOT / "src" / "applied" / "jobs_applied.json"

PROGRESS_JSON.parent.mkdir(parents=True, exist_ok=True)
APPLIED_ATS_PATH.parent.mkdir(parents=True, exist_ok=True)

_FILE_LOCK = threading.RLock()
_PRINT_LOCK = threading.RLock()


class BatchState:
    def __init__(self, target: int, max_time_sec: float, dry_run: bool = False):
        self.target = target
        self.max_time_sec = max_time_sec
        self.dry_run = dry_run
        self.start_time = time.time()
        self.total_processed = 0
        self.confirmed_count = 0
        self.submitted_unconfirmed_count = 0
        self.filled_count = 0
        self.skipped_dead_count = 0
        self.captcha_count = 0
        self.error_count = 0
        self.stop_requested = False
        self.results: list[dict[str, Any]] = []

    def is_done(self) -> bool:
        if self.stop_requested:
            return True
        if self.dry_run:
            if (self.filled_count + self.confirmed_count) >= self.target:
                return True
        else:
            if self.confirmed_count >= self.target:
                return True
        if (time.time() - self.start_time) >= self.max_time_sec:
            return True
        return False

    def elapsed_formatted(self) -> str:
        s = int(time.time() - self.start_time)
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        return f"{h:02d}:{m:02d}:{s:02d}"


def verify_authority() -> bool:
    if not AUTH_PATH.exists():
        print(f"[ERROR] Submit authority not found at {AUTH_PATH}")
        return False
    try:
        data = json.loads(AUTH_PATH.read_text(encoding="utf-8"))
        if data.get("allow_submit") is True or data.get("allow_submit_yes") is True:
            return True
    except Exception as e:
        print(f"[ERROR] Failed to read submit authority: {e}")
    return False


def record_audit(record: dict[str, Any]):
    with _FILE_LOCK:
        try:
            with open(AUDIT_JSONL, "a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")
        except Exception as e:
            print(f"[Warning] Failed writing audit log: {e}")


def record_applied_ledgers(ats: str, url: str, verification: str, company: str = "", title: str = ""):
    entry = {
        "company": company or ats,
        "role": title or "Software / AI / ML Engineer",
        "url": url,
        "platform": ats,
        "location": "India / Remote",
        "resume": "ML_Vision_RL (Resume ML_Vision_RL_PPO 7th Aug.pdf)",
        "status": "applied",
        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "verification": verification,
    }
    with _FILE_LOCK:
        for p in [APPLIED_ATS_PATH, APPLIED_MASTER_PATH]:
            try:
                data = json.loads(p.read_text(encoding="utf-8")) if p.exists() else []
            except Exception:
                data = []
            if not any(d.get("url") == url and d.get("status") == "applied" for d in data):
                data.append(entry)
                p.write_text(json.dumps(data, indent=2), encoding="utf-8")


def save_progress_summary(state: BatchState):
    with _FILE_LOCK:
        summary = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "elapsed": state.elapsed_formatted(),
            "target": state.target,
            "total_processed": state.total_processed,
            "confirmed_applied": state.confirmed_count,
            "submitted_unconfirmed": state.submitted_unconfirmed_count,
            "pass_filled_dry": state.filled_count,
            "skipped_dead": state.skipped_dead_count,
            "awaiting_human_captcha": state.captcha_count,
            "errors": state.error_count,
            "breakdown_by_ats": {
                "ashby": {
                    "confirmed": sum(1 for r in state.results if r.get("ats") == "ashby" and r.get("submit_status") == "CONFIRMED_APPLIED"),
                    "total": sum(1 for r in state.results if r.get("ats") == "ashby"),
                },
                "lever": {
                    "confirmed": sum(1 for r in state.results if r.get("ats") == "lever" and r.get("submit_status") == "CONFIRMED_APPLIED"),
                    "total": sum(1 for r in state.results if r.get("ats") == "lever"),
                },
                "greenhouse": {
                    "confirmed": sum(1 for r in state.results if r.get("ats") == "greenhouse" and r.get("submit_status") == "CONFIRMED_APPLIED"),
                    "total": sum(1 for r in state.results if r.get("ats") == "greenhouse"),
                },
            },
        }
        try:
            PROGRESS_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        except Exception as e:
            print(f"[Warning] Failed writing progress summary: {e}")


def worker_loop(worker_id: int, job_queue: list[dict], state: BatchState, do_submit: bool, headless: bool, cool_down_range: tuple[float, float]):
    while not state.is_done():
        job = None
        with _FILE_LOCK:
            if job_queue:
                job = job_queue.pop(0)
        if not job:
            break

        ats = job.get("ats") or job.get("platform") or ""
        url = job.get("url") or ""
        job_title = job.get("title", "")
        company = job.get("company") or job.get("org") or ""

        if not ats or not url:
            continue

        t0 = time.time()
        try:
            res = process_single_job(ats, url, headless=headless, do_submit=do_submit)
        except Exception as e:
            res = {
                "status": "WORKER_ERROR",
                "reason": str(e)[:150],
                "ats": ats,
                "url": url,
                "elapsed_sec": round(time.time() - t0, 2),
            }

        elapsed = res.get("elapsed_sec", round(time.time() - t0, 2))
        res["worker_id"] = worker_id
        res["company"] = company
        res["title"] = job_title
        res["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        status = res.get("status", "UNKNOWN")
        submit_status = res.get("submit_status", "")

        with _FILE_LOCK:
            state.total_processed += 1
            state.results.append(res)
            if submit_status == "CONFIRMED_APPLIED":
                state.confirmed_count += 1
                record_applied_ledgers(ats, url, res.get("verification", "Confirmed"), company=company, title=job_title)
            elif submit_status in ("SUBMIT_CLICKED_UNCONFIRMED", "SUBMIT_CLICKED_PENDING"):
                state.submitted_unconfirmed_count += 1
                # Still record in applied ledger with pending server echo tag
                record_applied_ledgers(ats, url, f"Pending echo: {submit_status}", company=company, title=job_title)
            elif submit_status == "AWAITING_HUMAN_CAPTCHA":
                state.captcha_count += 1
            elif status == "SKIPPED_DEAD":
                state.skipped_dead_count += 1
            elif status == "PASS_FILLED_100_PCT":
                state.filled_count += 1
            else:
                state.error_count += 1

        record_audit(res)
        save_progress_summary(state)

        with _PRINT_LOCK:
            tag = submit_status if submit_status else status
            print(
                f"[W{worker_id}] [{state.elapsed_formatted()}] "
                f"[Confirmed: {state.confirmed_count}/{state.target}] "
                f"[{ats.upper()}] {company} - {job_title[:30]} | {tag} "
                f"({res.get('filled_controls_count', 0)} controls, {elapsed}s) -> {url}",
                flush=True,
            )
            if submit_status == "AWAITING_HUMAN_CAPTCHA":
                print(f"   [!] CAPTCHA Detected on {url}: Saved snapshot to {res.get('screenshot')}", flush=True)

        if state.is_done():
            break

        # Fast Pacing Cool-Down (stealth jitter breather between applications)
        if submit_status == "AWAITING_HUMAN_CAPTCHA":
            cool_down = random.uniform(15.0, 25.0)
        else:
            cool_down = random.uniform(cool_down_range[0], cool_down_range[1])

        time.sleep(cool_down)


def main():
    parser = argparse.ArgumentParser(description="Fast ATS Submissions Runner")
    parser.add_argument("--queue", default=str(DEFAULT_QUEUE))
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--target", type=int, default=200)
    parser.add_argument("--hours", type=float, default=2.0)
    parser.add_argument("--headed", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--min-cool-down", type=float, default=3.0)
    parser.add_argument("--max-cool-down", type=float, default=6.5)
    args = parser.parse_args()

    workers = min(args.workers, 5)
    do_submit = not args.dry_run

    if do_submit:
        if not verify_authority():
            print("[CRITICAL] Missing valid submit authority in src/submit_permisssions! Aborting.")
            sys.exit(1)
        print(">>> LIVE SUBMIT MODE: Verified full authority in ashby_greenhouse_lever_submit_authority.json <<<", flush=True)
    else:
        print(">>> DRY-RUN MODE: Forms will be filled 100% and audited, but Submit will NOT be clicked <<<", flush=True)

    queue_file = Path(args.queue)
    if not queue_file.exists():
        print(f"[ERROR] Queue file not found: {queue_file}", flush=True)
        sys.exit(1)

    data = json.loads(queue_file.read_text(encoding="utf-8"))
    raw_jobs = data.get("jobs", []) if isinstance(data, dict) else data

    # Deduplicate against prior applied ledgers & audit records
    already_done = set()
    for p in [APPLIED_ATS_PATH, APPLIED_MASTER_PATH]:
        if p.exists():
            try:
                for item in json.loads(p.read_text(encoding="utf-8")):
                    if isinstance(item, dict) and "url" in item:
                        already_done.add(item["url"].strip().rstrip("/"))
            except Exception:
                pass

    if AUDIT_JSONL.exists():
        try:
            for line in AUDIT_JSONL.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    rec = json.loads(line)
                    u = rec.get("url", "").strip().rstrip("/")
                    sub_st = rec.get("submit_status", "")
                    st = rec.get("status", "")
                    if sub_st in ("CONFIRMED_APPLIED", "SUBMIT_CLICKED_UNCONFIRMED") or st == "SKIPPED_DEAD":
                        already_done.add(u)
        except Exception:
            pass

    unattempted_jobs = []
    for j in raw_jobs:
        u = j.get("url", "").strip().rstrip("/")
        if u and u not in already_done:
            unattempted_jobs.append(j)

    print(f"=== Fast ATS Submissions Runner ===", flush=True)
    print(f"Total Available Queue: {len(unattempted_jobs)} fresh unattempted jobs (filtered {len(already_done)} prior/dead)", flush=True)
    print(f"Target Submissions: {args.target}", flush=True)
    print(f"Workers: {workers} (Real Chrome Channel, Off-Screen Position)", flush=True)
    print(f"Fast Jitter Cool-Down: {args.min_cool_down}s - {args.max_cool_down}s", flush=True)
    print(f"Progress Ledger: {PROGRESS_JSON}", flush=True)
    print(f"Audit Trail: {AUDIT_JSONL}", flush=True)
    print("===================================\n", flush=True)

    total_sec = args.hours * 3600.0
    state = BatchState(target=args.target, max_time_sec=total_sec, dry_run=args.dry_run)
    cool_down_range = (args.min_cool_down, args.max_cool_down)

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futs = [
            executor.submit(
                worker_loop,
                wid,
                unattempted_jobs,
                state,
                do_submit,
                not args.headed,
                cool_down_range,
            )
            for wid in range(1, workers + 1)
        ]
        try:
            for fut in concurrent.futures.as_completed(futs):
                fut.result()
        except KeyboardInterrupt:
            print("\n[!] KeyboardInterrupt received. Wrapping up cleanly...")
            state.stop_requested = True

    save_progress_summary(state)
    print("\n================ FINAL BATCH SUMMARY ================", flush=True)
    print(f"Total Runtime: {state.elapsed_formatted()}", flush=True)
    print(f"Total Processed: {state.total_processed}", flush=True)
    print(f"Confirmed Applied: {state.confirmed_count}/{state.target}", flush=True)
    print(f"Submitted (Pending Echo): {state.submitted_unconfirmed_count}", flush=True)
    print(f"Awaiting Human CAPTCHA: {state.captcha_count}", flush=True)
    print(f"Skipped Dead/Closed: {state.skipped_dead_count}", flush=True)
    print(f"Errors: {state.error_count}", flush=True)
    print(f"Progress Saved: {PROGRESS_JSON}", flush=True)
    print(f"Audit Saved: {AUDIT_JSONL}", flush=True)
    print("=====================================================", flush=True)


if __name__ == "__main__":
    main()
