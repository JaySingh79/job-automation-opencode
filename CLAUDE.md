# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A **general job-application automation harness**. The goal is to auto-fill any online job
application — Workday, Phenom, Greenhouse, Lever, Ashby, iCIMS, Taleo, a hand-rolled careers form —
without a human retyping the same forty fields. Workday is the first ATS it learned, not the scope.

## The 2026-08-02 Gartner run — what actually happened

Req 110911 on `gartner.wd5/EXT`. **The run went correctly. Nothing was auto-submitted.**

- "Save and Continue" was **not** the submit button.
- The automation filled every step and stopped, leaving the final review page open.
- That review page had its own Submit button, and **the human clicked it** from Firecrawl's Live
  View, after reviewing the filled application.

G1 did its job. It is a standing precaution, not a post-mortem: submitting an application is the one
irreversible action in the whole flow — it cannot be unsent, and on an unmapped ATS the terminal step
is not knowable in advance. So the last click always belongs to a human, on every driver, on every
ATS. That is the load-bearing invariant of this repo.

⚠️ **The old record was wrong and is still wrong in other files.** Several places in this repo
(`execution_instruction.md`, `apply_session.py`, `guards.py`, `user_profile.json`, `kb/graph.json` →
`pitfall:A1` → `kb/GRAPH.md`) still say the application was "submitted without human review" because
step 4's continue was the submit. That did not happen. Do not repeat that claim, and do not use it as
justification when writing new code or docs. Correcting it properly means editing `kb/graph.json`
(the source of truth) and re-projecting/re-rendering — not hand-editing `kb/GRAPH.md`.

### What is actually known vs. assumed

Exactly **one** ATS has been driven end to end (Workday, one tenant, one requisition). Everything
Workday-shaped in this codebase is the first instance of a pattern, not the pattern itself.

- `runs/example-greenhouse.json` is a schema fixture. No Greenhouse application has ever been run.
- `HPE` in `job_links.json` (`careers.hpe.com`, Phenom) is queued, not yet attempted.
- Any selector, step count, constraint, or terminal-step claim for a non-Workday ATS is
  **unverified** until a live run pays for it.

So do not generalise from the Workday flow. When a new ATS is attempted, expect to learn its shape
from scratch, and write down what you learn (see *Per-ATS knowledge folders*).

## Two drivers — the user picks, never assume

Browser work can run in either of two places. The command surface is nearly the same; the
constraints are not. **Ask which one, or use the one the user named. Do not default silently.**

| | Firecrawl cloud | agent-browser local |
|---|---|---|
| How | `firecrawl scrape --profile` + `firecrawl interact` | `agent-browser open/snapshot/fill/click` |
| Runs on | Firecrawl's remote sandbox | this machine, local Chrome over CDP |
| Cost | credits (see budget rule) | free |
| Session life | dies after ~10 min idle; billed while open | background daemon, `--idle-timeout` default 1h |
| Login state | `--profile <name>`, single writer | real Chrome profile (`--profile Default`) or auth vault |
| Files | must be fetched *inside* the sandbox | local paths work directly |
| Human review | Live View URL | the actual browser window (`--headed`), `agent-browser dashboard` on :4848 |

`agent-browser` is **already** used inside the Firecrawl path — the cloud sandbox ships the same CLI,
which is why `guards.py:85` and `apply_orchestrator.py:343` emit `agent-browser upload` / `eval`
strings. "Cloud" vs "local" is about *where the CLI runs*, not which CLI. Command reference lives in
`.agents/skills/agent-browser/SKILL.md`; the version-matched guide is `agent-browser skills get core`.

No local Playwright in the live path — that ban stands. agent-browser is CDP, not Playwright.

**Guards do not relax on the local driver.** G1, G2, G5 and G7 are about the application, not the
transport. Only the credit budget and G4 (session batching) are Firecrawl-specific — a local session
costs nothing and does not idle out at ten minutes, so batching there is a nicety, not a rule.

One thing the local driver changes for the better: handing off for human review is just the browser
window. Leave it open on the review page and tell the user; no Live View link needed.

## Per-ATS knowledge folders

Each ATS gets its own folder under `ats/`. One folder per **ATS product**, not per employer —
tenants of the same product share a flow.

```
ats/
  README.md            # the convention, in short
  workday/
    NOTES.md           # prose memory: flow shape, surprises, what to check next time
    *.json             # raw captures and pending observations for this ATS
  phenom/              # created the first time an HPE-style posting is attempted
  greenhouse/
```

Rules that keep this from becoming a second source of truth:

- `NOTES.md` is **memory, not config**. No code reads it. It records what a human or agent would
  otherwise have to rediscover: how many steps, what the terminal step is actually called, which
  fields are searchable prompts, what error text looks like, which driver worked, what it cost.
- `kb/graph.json` remains **the only source of truth for anything code reads** — selectors, answers,
  constraints, `terminal_submit_step`. When an observation in `NOTES.md` becomes actionable, fold it
  into the graph via `kb/harvest.py` and let the projection carry it. Never teach the orchestrator
  from a notes file.
- JSON in an ATS folder is either a raw capture (evidence, keep it) or a pending observation awaiting
  harvest. Once harvested, the graph wins; don't hand-maintain both.
- Write the folder **during or immediately after** the run, while the session is still fresh. A
  pitfall you don't write down gets paid for twice — and, as the A1 entry shows, a pitfall written
  down wrong is worse than none.

## Commands

All Python goes through the venv. Package installs go through `uv`, never raw `pip`.

```powershell
.venv\Scripts\python.exe preflight.py                      # gate, 0 credits; exit 1 = blocked
.venv\Scripts\python.exe preflight.py --no-probe           # skip host curl probes (offline/tests)
.venv\Scripts\python.exe kb\project.py tenant:gartner.wd5/EXT   # graph -> field_map.json + guards.json

# selector-free driver (ATS-agnostic, prompt-based) — prefer this for a new ATS
.venv\Scripts\python.exe apply_session.py --job HPE --dry-run
.venv\Scripts\python.exe apply_session.py --job HPE
.venv\Scripts\python.exe apply_session.py --job HPE --resume-session <scrape-id>

# selector-driven orchestrator (Workday-specific today)
$env:JOB="Gartner"; $env:DRY_RUN="1"; .venv\Scripts\python.exe apply_orchestrator.py   # 0 credits
$env:JOB="Gartner"; Remove-Item Env:DRY_RUN; .venv\Scripts\python.exe apply_orchestrator.py  # live, stops at G1

.venv\Scripts\python.exe kb\harvest.py runs\<run>.json     # fold a run back in + regenerate GRAPH.md
.venv\Scripts\python.exe kb\harvest.py --render-only       # regenerate GRAPH.md only

uv pip install -r requirements.txt
```

Local-driver equivalents (0 credits, real Chrome):

```powershell
agent-browser --profile Default --headed open <job-url>
agent-browser snapshot -i          # accessibility tree with @eN refs
agent-browser fill @e12 "value"
agent-browser skills get core      # version-matched usage guide, read before driving
```

Tests — 50, no network, no credits:

```powershell
.venv\Scripts\python.exe -m pytest testing_files\test_guards.py -q
.venv\Scripts\python.exe -m pytest testing_files\test_guards.py -q -k terminal_step   # single test / group
```

Always name `testing_files/test_guards.py`. It sits one directory below the code it imports, so its
`ROOT` climbs two parents — run it from the repo root. `testing_files/test_crawl.py` and
`testing_files/testing.py` are throwaway probes from the pre-Firecrawl era — `test_`-prefixed but not
pytest tests, and `test_crawl.py` imports `crawl4ai`. Bare `pytest` will try to collect them.
`test_crawl.py` reads its LinkedIn session cookie from `LI_AT`; never paste one back in.

Env: `.env` holds `FIRECRAWL_API_KEY`. `firecrawl` CLI must be on PATH (v1.19.27 observed);
`agent-browser` likewise (v0.27.0 observed).

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
- `apply_orchestrator.py` — **selector-driven, Workday-shaped.** The step scripts
  (`STEP1`..`STEP4_FILL_ONLY`) are `%`-formatted Python or bash sent verbatim into the Firecrawl
  sandbox. `%`-literals inside them must be `%%`.
- `apply_session.py` — **selector-free, ATS-agnostic.** Drives one live session with
  natural-language `interact --prompt` steps, so the browser's own agent resolves fields and adding
  a job means adding a URL. Enforces G1 by regex on every outgoing instruction (`SUBMIT_WORDS`) and
  owns the session as a context manager, because a leaked session keeps billing *and* holds the
  profile's single writer lock. This is the path that scales to hundreds of postings; the
  orchestrator is the path that is precise about one known flow.

The layering is what makes a second application cheap: canonical fields and the answer bank are
universal, constraints are per-ATS-product, selectors are per-tenant. Adding a tenant must not touch
the `selector:tenant:gartner*` subtree — `test_harvest_grows_shared_layers_*` enforces that.

## Hard rules

- **G1 / submit boundary.** `guards.terminal_step_guard` refuses to click continue on the terminal
  step; `apply_session.py` refuses to *send* any instruction containing a commit word. `ALLOW_SUBMIT=1`
  is the only override and exists for a human to type — automation never sets it. An unknown
  `terminal_submit_step` (a new tenant, a new ATS) is treated as destructive and blocks every
  continue click. That is intended, not a bug to route around. Applies on both drivers.
  The end state of a successful run is a filled application sitting on its review page with a human
  looking at it. That is success, not an incomplete run.
- **G2 / upload integrity.** Verify magic bytes *and* exact byte count before the file reaches the
  page. A 2.6 KB HTML error page once uploaded cleanly as `resume.pdf`. On the cloud driver the check
  must happen *inside* the sandbox and the tmpfiles token is IP-bound, so resolve it there with
  `curl` — `urllib` gets 403. On the local driver the file is already local; still verify.
- **G4 / session batching.** Firecrawl only: one batched `interact` call per form step, because live
  sessions die after ~10 min idle and bill while open.
- **G5 / never block with a session open.** Queue unanswered questions via `QuestionQueue.ask` and
  report once at the end. Asking mid-run has already cost two sessions. Applies on both drivers.
- **G7 / never type into a dropdown.** Enumerate the field's own options and fuzzy-match
  (`resolve_option`, floor 0.72). Below the floor, queue a question instead of guessing. Applies on
  both drivers.
- Budget (Firecrawl only): cap 150 credits/run, abort below 200 remaining. `scrape` = 1,
  `interact` ≈ 2, `parse` ≈ 1/page, `--query` = +5 and is banned.

## Gotchas that cost a run

Universal:

- One writer per Firecrawl `--profile`; concurrent readers need `--no-save-changes`. A leaked
  session blocks the next attempt with "Another session is currently writing to this profile".
- A honeypot input ("for robots only") is present on Workday and is common elsewhere — `is_honeypot`
  must gate any generic fill loop.
- `interact --python -c` compiles with `mode="single"` and executes **only the first statement**,
  returning rc=0 while silently dropping the rest. `--node` runs full scripts but discards stdout.
  Prompts are the only mode that both acts and reports.
- `job_links.json` has no enclosing braces on purpose — both drivers read it as
  `json.loads("{" + text.rstrip(",") + "}")`. It looks malformed to a bare `json.load`. Don't "fix" it.
- agent-browser `@eN` refs go stale after any DOM change: snapshot, then act, then re-snapshot.

Workday-specific (do **not** assume these hold on a new ATS — verify and record in `ats/<name>/NOTES.md`):

- Validation errors are **not** in `errorMessage`, `role=alert`, or `aria-invalid` text. The only
  reliable read is `innerText` lines starting with `Error` (`harvest_errors`).
- `data-automation-id` sits on wrapper `div`s — descend to `input`/`textarea`/`button`.
- Searchable prompts don't filter when you type into the field; go through `promptSearchButton`
  → the Search box → Enter.
- LinkedIn URLs must contain `www.` or Workday rejects them (`validate` autofixes this).
- Role Description rejects `< > [ ] { } " \` as "illegal characters" — `sanitize` rewrites `>90%`
  to `over 90%` rather than deleting the claim.

## Conventions

- Comments explain *why* a line exists (which pitfall it prevents), not what it does. Match that.
  If the "why" is an incident, make sure the incident is recorded accurately — see the A1 correction
  above.
- `execution_instruction_firecrawl.md` is the runbook — operating procedure only, no field data. The
  name carries the driver because the procedure is Firecrawl-specific; the local driver's is not
  written yet.
- `kb/GRAPH.md` is generated. Edit the graph and re-render; never edit it directly.
- The per-ATS notes file is `NOTES.md` under `ats/workday/` and `observation_importance.md` under the
  folders written later (`oracle-recruiting`, `google-forms`, `microsoft-forms`). Both are the same
  thing — hand-written memory, never generated. `kb/GRAPH.md` is generated and never hand-written. If
  a fact belongs to code, it goes in the graph, not the notes.
- `necessary_browsing_automation/` holds driver-agnostic browsing notes — `browser_crawling_guidelines.md`
  and a Gemini transcript kept as raw evidence. Prose only; no code reads it.
- `steel_based_automation/PLAN.md` is a proposal for a third driver (Steel). Nothing in it is built.
- `pure_firecrawl_cloud_automation_plan.md` is a superseded design doc kept for history; the file it
  proposes (`pure_firecrawl_automation.py`) does not exist and should not be created. Its title is
  also now misleading — Firecrawl is one of two drivers, not the whole approach.
- `.agents/skills/agent-browser/SKILL.md` carries a snapshot of the agent-browser command reference.
  When it disagrees with `agent-browser skills get core --full`, the CLI wins.
- `.firecrawl/` is a scratch cache of live-session probe scripts and outputs, gitignored except where
  noted. `.firecrawl/field_map.handwritten.json` is the pre-projection baseline that
  `test_projection_round_trips_the_handwritten_map` compares against — don't delete it.
