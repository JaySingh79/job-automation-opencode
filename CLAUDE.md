# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A job-application automation harness that drives a Workday "EXT" apply flow entirely through
Firecrawl's **cloud** browser (`firecrawl scrape --profile` + `firecrawl interact`). No local
Playwright in the live path. Every guard and selector in the codebase exists because a live run
paid for it once; `kb/GRAPH.md` records the pitfall behind each.

The 2026-08-02 Gartner run (req 110911) was **submitted without human review** because step 4's
"Save and Continue" turned out to be the submit. That incident is why G1 exists. Treat the submit
boundary as the load-bearing invariant of this repo.

## Commands

All Python goes through the venv. Package installs go through `uv`, never raw `pip`.

```powershell
.venv\Scripts\python.exe preflight.py                      # gate, 0 credits; exit 1 = blocked
.venv\Scripts\python.exe preflight.py --no-probe           # skip host curl probes (offline/tests)
.venv\Scripts\python.exe kb\project.py tenant:gartner.wd5/EXT   # graph -> field_map.json + guards.json
$env:DRY_RUN="1"; .venv\Scripts\python.exe apply_orchestrator.py   # print every step's script, 0 credits
Remove-Item Env:DRY_RUN; .venv\Scripts\python.exe apply_orchestrator.py  # live, stops at G1
.venv\Scripts\python.exe kb\harvest.py runs\<run>.json     # fold a run back in + regenerate GRAPH.md
.venv\Scripts\python.exe kb\harvest.py --render-only       # regenerate GRAPH.md only

uv pip install -r requirements.txt
```

Tests — 39, no network, no credits:

```powershell
.venv\Scripts\python.exe -m pytest test_guards.py -q
.venv\Scripts\python.exe -m pytest test_guards.py -q -k terminal_step   # single test / group
```

Always name `test_guards.py`. `test_crawl.py`, `test_playwright_bypass.py` and
`test_playwright_workday_dom.py` are throwaway probes from the pre-Firecrawl era — `test_`-prefixed
but not pytest tests, and they import `crawl4ai`/`playwright`. Bare `pytest` will try to collect them.

Env: `.env` holds `FIRECRAWL_API_KEY`. `firecrawl` CLI must be on PATH (v1.19.27 observed).

## Architecture

One direction of data flow. Do not shortcut it.

```
kb/graph.json  --kb/project.py-->  field_map.json + guards.json  -->  apply_orchestrator.py
     ^                                                                      |
     +----------------- kb/harvest.py runs/<run>.json <---------------------+
```

**`kb/graph.json` is the only source of truth.** `field_map.json` and `guards.json` are generated
projections — hand-edits are lost on the next `kb/project.py`. `guards.json` is gitignored. To change
a selector, an answer, a constraint, or which step submits, edit the graph (via `kb/seed_gartner.py`,
a run file + `harvest.py`, or the `Graph` API), then re-project.

- `kb/kb.py` — node/edge store over plain JSON. Node types and edge rels are whitelisted; unknown
  ones raise. **Nodes are never deleted.** A material attr change clones the old node as `id@date`
  and links `superseded_by`, so a tenant silently changing its DOM leaves a trail.
  `find_answer()` is the compounding lever: `max(SequenceMatcher ratio, content-word containment)`
  at `THRESHOLD = 0.78`, so the same screening question reworded by another ATS still resolves.
  Answers whose edge carries `employer_specific` are locked to their tenant — "Are you currently
  employed by Gartner?" must not answer Acme's form.
- `kb/harvest.py` — merges a run file into the graph and re-renders `GRAPH.md`. The run-file schema
  is documented in `harvest()`'s docstring; `runs/example-greenhouse.json` is the working reference.
  Appends to `kb/events.jsonl` first (append-only, never rewritten) so a bad merge is reconstructable.
- `kb/project.py` — flattens the graph into the two files the orchestrator reads. Screening answers
  become `q.*` keys, which is exactly what the orchestrator greps for.
- `guards.py` — guard *implementations*; the rules they enforce come from `guards.json`.
- `preflight.py` — G9/G8/C4 gate. Runs automatically inside a live orchestrator run unless
  `SKIP_PREFLIGHT=1`. `--warn-only` downgrades blockers.
- `apply_orchestrator.py` — the step scripts (`STEP1`..`STEP4_FILL_ONLY`) are `%`-formatted Python
  or bash sent verbatim into the Firecrawl sandbox. `%`-literals inside them must be `%%`.

The layering is what makes a second application cheap: canonical fields and the answer bank are
universal, constraints are per-ATS-product, selectors are per-tenant. Adding a tenant must not touch
the `selector:tenant:gartner*` subtree — `test_harvest_grows_shared_layers_*` enforces that.

## Hard rules

- **G1 / submit boundary.** `guards.terminal_step_guard` refuses to click continue on the terminal
  step. `ALLOW_SUBMIT=1` is the only override and exists for a human to type — automation never sets
  it. An unknown `terminal_submit_step` (a new tenant) is treated as destructive and blocks every
  continue click. That is intended, not a bug to route around.
- **G2 / upload integrity.** Verify magic bytes *and* exact byte count inside the sandbox before the
  file reaches the page. A 2.6 KB HTML error page once uploaded cleanly as `resume.pdf`. The
  tmpfiles token is IP-bound, so resolve it in the sandbox with `curl` — `urllib` gets 403.
- **G4 / session batching.** One batched `interact` call per form step. Live sessions die after
  ~10 min idle.
- **G5 / never block with a session open.** Queue unanswered questions via `QuestionQueue.ask` and
  report once at the end. Asking mid-run has already cost two sessions.
- **G7 / never type into a dropdown.** Enumerate the field's own options and fuzzy-match
  (`resolve_option`, floor 0.72). Below the floor, queue a question instead of guessing.
- Workday validation errors are **not** in `errorMessage`, `role=alert`, or `aria-invalid` text.
  The only reliable read is `innerText` lines starting with `Error` (`harvest_errors`).
- Budget: cap 150 credits/run, abort below 200 remaining. `scrape` = 1, `interact` ≈ 2,
  `parse` ≈ 1/page, `--query` = +5 and is banned.

## Gotchas that cost a run

- `data-automation-id` sits on wrapper `div`s — descend to `input`/`textarea`/`button`.
- Searchable prompts don't filter when you type into the field; go through `promptSearchButton`
  → the Search box → Enter.
- LinkedIn URLs must contain `www.` or Workday rejects them (`validate` autofixes this).
- Role Description rejects `< > [ ] { } " \` as "illegal characters" — `sanitize` rewrites `>90%`
  to `over 90%` rather than deleting the claim.
- One writer per Firecrawl `--profile`; concurrent readers need `--no-save-changes`.
- A honeypot input ("for robots only") is present — `is_honeypot` must gate any generic fill loop.

## Conventions

- Comments explain *why* a line exists (which pitfall it prevents), not what it does. Match that.
- `execution_instruction.md` is the runbook — operating procedure only, no field data.
- `kb/GRAPH.md` is generated. Edit the graph and re-render; never edit it directly.
- `pure_firecrawl_cloud_automation_plan.md` is a superseded design doc kept for history; the file it
  proposes (`pure_firecrawl_automation.py`) does not exist and should not be created.
- `.firecrawl/` is a scratch cache of live-session probe scripts and outputs, gitignored except where
  noted. `.firecrawl/field_map.handwritten.json` is the pre-projection baseline that
  `test_projection_round_trips_the_handwritten_map` compares against — don't delete it.
