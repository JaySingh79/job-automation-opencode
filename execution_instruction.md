# Runbook

Field data, selectors, guards, pitfalls and the answer bank now live in the memory
graph. This file is the operating procedure only.

- **Knowledge:** `kb/graph.json` (source of truth) · `kb/GRAPH.md` (readable view)
- **Generated:** `field_map.json`, `guards.json` — do not hand-edit, they are overwritten
- **Provenance:** `kb/events.jsonl`, append-only

---

## Procedure

```powershell
# 1. gate — 0 credits. Blocks on resume/profile mismatch or ambiguous profile values.
.venv\Scripts\python.exe preflight.py

# 2. project the graph down to what the orchestrator reads
.venv\Scripts\python.exe kb\project.py tenant:gartner.wd5/EXT

# 3. dry run — builds every step's script, spends nothing
$env:DRY_RUN="1"; .venv\Scripts\python.exe apply_orchestrator.py

# 4. live run — stops at the submit boundary and hands you the command
Remove-Item Env:DRY_RUN; .venv\Scripts\python.exe apply_orchestrator.py

# 5. fold what was learned back into the graph
.venv\Scripts\python.exe kb\harvest.py runs\<run>.json
```

Steps 1 and 3 are gates, not options. Step 1 runs automatically inside step 4 unless
`SKIP_PREFLIGHT=1`.

## Verify at each step

| Step | Expect |
|---|---|
| 1 | exit 0. Exit 1 lists what to reconcile. |
| 2 | `36 fields, terminal submit step = 4` |
| 3 | one `--- DRY_RUN ---` block per step, credits unchanged |
| 4 | `G1 SUBMIT BOUNDARY` banner and a submit one-liner |
| 5 | `+N nodes, +N edges`, `kb/GRAPH.md` regenerated |

```powershell
.venv\Scripts\python.exe -m pytest test_guards.py -q   # 39 tests, no network
```

## The submit boundary

**This tenant has no separate Submit button.** `pageFooterNextButton` on step 4
(Voluntary Disclosures) submits. Step 5 "Review" is a post-submit confirmation screen.
G1 refuses to click it. `ALLOW_SUBMIT=1` is the only override and exists for a human to
type, never for automation to set.

Per-tenant boundaries are listed in `kb/GRAPH.md` under *Submit boundaries*.

## Budget

Cap 150 credits, abort below 200 remaining. Measured rates: `scrape` 1, `parse` ~1/page,
`interact` ~2, `--query` +5 (banned). The 2026-08-02 run cost 66.

## Adding an application

1. Point `job_links.json` at the new posting.
2. Run the procedure. Unknown tenants have no `terminal_submit_step`, so G1 blocks every
   continue click until the flow is mapped — that is intended.
3. Write a run file (`runs/example-greenhouse.json` is the shape reference) and harvest it.

Screening questions resolve from the answer bank automatically. Questions naming a
specific employer stay locked to the tenant they were observed on; everything else
transfers. Anything unmatched is queued by G5 and asked once, after the session closes.

## History

The 2026-08-02 Gartner application (req 110911) was **submitted** — status In Process —
without the intended human review, because step 4's continue turned out to be the submit.
That incident and 29 other findings are recorded as pitfall nodes, each linked to the
guard that now prevents it. See `kb/GRAPH.md`.
