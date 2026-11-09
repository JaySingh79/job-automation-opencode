"""
Universal ATS 200-Batch Submissions Runner.
Executes 200 applications across Ashby, Lever, and Greenhouse within a 3-hour window
using 4 concurrent Patchright workers with deep human-emulation and anti-bot escape policies.
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

# Ensure local imports work cleanly
ROOT = Path(r"D:\Projects\PRACTICE\firecrawl_test")
sys.path.insert(0, str(ROOT))

from src.scripts.universal_ats_filler import (
    process_single_job,
    CANDIDATE,
    PROGRESS_DIR,
    SNAP_DIR,
)

AUTH_PATH = ROOT / "src" / "submit_permisssions" / "ashby_greenhouse_lever_submit_authority.json"
QUEUE_PATH = ROOT / "src" / "job_search_results" / "ashby_lever_greenhouse" / "2026-11-06-fresh-200-queue.json"
PROGRESS_JSON = PROGRESS_DIR / "ashby_lever_greenhouse" / "2026-11-06-200-batch-progress.json"
AUDIT_JSONL = PROGRESS_DIR / "ashby_lever_greenhouse" / "2026-11-06-200-submit-audit.jsonl"
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
        self.confirmed_count = 0
        self.submitted_unconfirmed_count = 0
        self.filled_count = 0
        self.skipped_dead_count = 0
        self.captcha_count = 0
        self.error_count = 0
        self.total_processed = 0
        self.stop_requested = False
        self.results: list[dict[str, Any]] = []

    def is_done(self) -> bool:
        if self.stop_requested:
            return True
        if self.dry_run:
            if (self.filled_count + self.skipped_dead_count + self.error_count) >= self.target:
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
        return f"{h:02d}h {m:02d}m {s:02d}s"


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


def record_applied_ledgers(ats: str, url: str, verification: str):
    parts = url.split("://")[-1].split("/")
    company = parts[1] if len(parts) > 1 else ats
    entry = {
        "company": company,
        "role": "Software / AI / ML Engineer",
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


def worker_loop(worker_id: int, job_queue: list[dict], state: BatchState, do_submit: bool, headless: bool, pacing_interval: float):
    while not state.is_done():
        job = None
        with _FILE_LOCK:
            if job_queue:
                job = job_queue.pop(0)
        if not job:
            break

        ats = job["ats"]
        url = job["url"]
        job_title = job.get("title", "")
        company = job.get("company", "")

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
        res["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Status categorization
        status = res.get("status", "UNKNOWN")
        submit_status = res.get("submit_status", "")

        with _FILE_LOCK:
            state.total_processed += 1
            state.results.append(res)
            if submit_status == "CONFIRMED_APPLIED":
                state.confirmed_count += 1
                record_applied_ledgers(ats, url, res.get("verification", "Confirmed"))
            elif submit_status in ("SUBMIT_CLICKED_UNCONFIRMED", "SUBMIT_CLICKED_PENDING"):
                state.submitted_unconfirmed_count += 1
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
                f"[{ats.upper()}] {tag} "
                f"({res.get('filled_controls_count', 0)} controls, {elapsed}s) -> {url}",
                flush=True,
            )
            if submit_status == "AWAITING_HUMAN_CAPTCHA":
                print(f"   [!] CAPTCHA Detected on {url}: Saved snapshot to {res.get('screenshot')}", flush=True)

        if state.is_done():
            break

        # Anti-Bot Pacing & Jitter Cool-Down:
        if state.dry_run:
            cool_down = random.uniform(3.0, 6.0)
        elif status == "SKIPPED_DEAD" or elapsed < 15.0:
            cool_down = random.uniform(15.0, 30.0)
        elif submit_status == "AWAITING_HUMAN_CAPTCHA":
            cool_down = random.uniform(40.0, 70.0)
        else:
            base_wait = max(30.0, min(160.0, pacing_interval - elapsed))
            cool_down = base_wait + random.uniform(-10.0, 20.0)

        time.sleep(max(3.0, cool_down))


def main():
    parser = argparse.ArgumentParser(description="Universal ATS 200 Submissions in 3 Hours")
    parser.add_argument("--queue", default=str(QUEUE_PATH))
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--target", type=int, default=200)
    parser.add_argument("--hours", type=float, default=3.0)
    parser.add_argument("--headed", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    workers = min(args.workers, 5)
    do_submit = not args.dry_run

    if do_submit:
        if not verify_authority():
            print("[CRITICAL] Missing valid submit authority in src/submit_permisssions! Aborting.")
            sys.exit(1)
        print(">>> LIVE SUBMIT MODE: Verified authority in ashby_greenhouse_lever_submit_authority.json <<<", flush=True)
    else:
        print(">>> DRY-RUN MODE: Forms will be filled 100% and audited, but Submit will NOT be clicked <<<", flush=True)

    queue_file = Path(args.queue)
    if not queue_file.exists():
        print(f"[ERROR] Queue file not found: {queue_file}", flush=True)
        sys.exit(1)

    queue_data = json.loads(queue_file.read_text(encoding="utf-8"))
    target_pool = queue_data.get("target", [])
    backup_pool = queue_data.get("backup", [])
    raw_jobs = list(target_pool) + list(backup_pool)

    # Filter out jobs already submitted or permanently dead from audit and applied ledgers
    already_done = set()
    if AUDIT_JSONL.exists():
        for line in AUDIT_JSONL.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    rec = json.loads(line)
                    u = rec.get("url", "").strip().rstrip("/")
                    sub_st = rec.get("submit_status", "")
                    st = rec.get("status", "")
                    if sub_st in ("CONFIRMED_APPLIED", "SUBMIT_CLICKED_UNCONFIRMED") or st == "SKIPPED_DEAD":
                        already_done.add(u)
                except Exception:
                    pass
    if APPLIED_MASTER_PATH.exists():
        try:
            for item in json.loads(APPLIED_MASTER_PATH.read_text(encoding="utf-8")):
                if isinstance(item, dict) and "url" in item:
                    already_done.add(item["url"].strip().rstrip("/"))
        except Exception:
            pass

    all_jobs = [j for j in raw_jobs if j.get("url", "").strip().rstrip("/") not in already_done]

    print(f"=== Universal ATS 200 Runner ===", flush=True)
    print(f"Total Available Queue: {len(all_jobs)} fresh unattempted jobs (filtered {len(already_done)} prior/dead)", flush=True)
    print(f"Target Submissions: {args.target}", flush=True)
    print(f"Operational Window: {args.hours} hours ({int(args.hours * 3600)} seconds)", flush=True)
    print(f"Workers: {workers} (Real Chrome Channel, Off-Screen Position)", flush=True)

    # Compute target pacing interval per worker
    total_sec = args.hours * 3600.0
    jobs_per_worker = args.target / workers
    pacing_interval = total_sec / jobs_per_worker  # e.g. 10800 / (200 / 4) = 216s per job per worker

    print(f"Target Pacing Interval: ~{round(pacing_interval, 1)}s per job per worker", flush=True)
    print(f"Progress Ledger: {PROGRESS_JSON}", flush=True)
    print(f"Audit Trail: {AUDIT_JSONL}", flush=True)
    print("===================================\n", flush=True)

    state = BatchState(target=args.target, max_time_sec=total_sec, dry_run=args.dry_run)

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futs = [
            executor.submit(
                worker_loop,
                wid,
                all_jobs,
                state,
                do_submit,
                not args.headed,
                pacing_interval,
            )
            for wid in range(1, workers + 1)
        ]
        try:
            for fut in concurrent.futures.as_completed(futs):
                fut.result()
        except KeyboardInterrupt:
            print("\n[!] KeyboardInterrupt received. Requesting workers to wrap up current jobs cleanly...")
            state.stop_requested = True

    save_progress_summary(state)
    print("\n================ FINAL BATCH SUMMARY ================", flush=True)
    print(f"Total Runtime: {state.elapsed_formatted()}", flush=True)
    print(f"Total Processed: {state.total_processed}", flush=True)
    print(f"Confirmed Applied: {state.confirmed_count}/{state.target}", flush=True)
    print(f"Submitted (Awaiting Server Echo): {state.submitted_unconfirmed_count}", flush=True)
    print(f"Dry-Filled (Pass 100%): {state.filled_count}", flush=True)
    print(f"Awaiting Human CAPTCHA: {state.captcha_count}", flush=True)
    print(f"Skipped Dead/Closed: {state.skipped_dead_count}", flush=True)
    print(f"Errors: {state.error_count}", flush=True)
    print(f"Progress Saved: {PROGRESS_JSON}", flush=True)
    print(f"Audit Saved: {AUDIT_JSONL}", flush=True)
    print("=====================================================", flush=True)


if __name__ == "__main__":
    main()
