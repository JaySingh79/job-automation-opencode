# Runbook

Field data, selectors, guards, pitfalls and the answer bank live in
`user_profile.json`, `field_map.json`, `guards.json` and `ats/*/` notes.
This file is the operating procedure only.

- **Knowledge:** `user_profile.json` (answer bank) · `field_map.json` (per-tenant selectors) · `guards.json` (guard rules) · `ats/*/` (per-ATS notes)
- **Generated:** nothing — `field_map.json` and `guards.json` are hand-maintained

---

## Procedure

```powershell
# 1. gate — 0 credits. Blocks on resume/profile mismatch or ambiguous profile values.
.venv\Scripts\python.exe preflight.py

# 2. dry run — builds every step's script, spends nothing
$env:DRY_RUN="1"; .venv\Scripts\python.exe apply_orchestrator.py

# 3. live run — stops at the submit boundary and hands you the command
Remove-Item Env:DRY_RUN; .venv\Scripts\python.exe apply_orchestrator.py

# 4. fold what was learned back into ats/<product>/NOTES.md + guards.json
```

Steps 1 and 2 are gates, not options. Step 1 runs automatically inside step 3 unless
`SKIP_PREFLIGHT=1`.

## Verify at each step

| Step | Expect |
|---|---|
| 1 | exit 0. Exit 1 lists what to reconcile. |
| 2 | one `--- DRY_RUN ---` block per step, credits unchanged |
| 3 | `G1 SUBMIT BOUNDARY` banner and a submit one-liner |
| 4 | `ats/<product>/NOTES.md` updated, `guards.json` updated if a rule changed |

```powershell
.venv\Scripts\python.exe -m pytest test_guards.py -q   # 39 tests, no network
```

## The submit boundary

**This tenant has no separate Submit button.** `pageFooterNextButton` on step 4
(Voluntary Disclosures) submits. Step 5 "Review" is a post-submit confirmation screen.
G1 refuses to click it. `ALLOW_SUBMIT=1` is the only override and exists for a human to
type, never for automation to set.

Per-tenant boundaries are listed in `ats/workday/NOTES.md` under *Submit boundaries*.

## Budget

Cap 150 credits, abort below 200 remaining. Measured rates: `scrape` 1, `parse` ~1/page,
`interact` ~2, `--query` +5 (banned). The 2026-08-02 run cost 66.

## Adding an application

1. Point `job_links.json` at the new posting.
2. Run the procedure. Unknown tenants have no `terminal_submit_step`, so G1 blocks every
   continue click until the flow is mapped — that is intended.
3. Write down what the run taught in `ats/<product>/NOTES.md` (flow shape, quirks, traps)
   and update `guards.json` / `field_map.json` if a rule or selector changed.

Screening questions resolve from the answer bank automatically. Questions naming a
specific employer stay locked to the tenant they were observed on; everything else
transfers. Anything unmatched is queued by G5 and asked once, after the session closes.

## History

The 2026-08-02 Gartner application (req 110911) went correctly — filled and stopped
for human review. Past incidents are recorded in `ats/workday/NOTES.md`, each linked to the
guard that now prevents it.
