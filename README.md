# Job-Application Automation Harness

Fill job applications with AI agents — cheaply, in parallel, without losing the plot.
One posting = one form session. The automation fills everything safely answerable and
stops on the review page. **The final Submit always belongs to a human.**

Built on [OpenCode](https://opencode.ai) orchestration, Playwright browser automation,
Firecrawl cloud extraction, portal-specific subagents, and a knowledge graph over the
lessons each run teaches.

## Quickstart (the easy way)

```bash
git clone <this-repo> && cd <this-repo>
opencode            # install it first if you haven't: https://opencode.ai
```

Then in the session, launch a fill with:

```text
@initiate_fill.md <paste the job link here>
```

That's it — the prompt routes to background recon (`job-intel`) and then the matching
portal agent, which fills the application and stops on the review page for your Submit.

## Skills that quietly balance it all

- **Task Observer** — watches multi-step runs for reusable patterns worth preserving.
- **Playwright** — browser automation via CLI (token-cheap) and MCP server (stateful,
  accessibility-tree driven), plus the browser extension for your real logged-in Chrome.
- **Firecrawl** — discovery + extraction side: job listings become structured workload
  before any browser agent starts crawling.
- **Knowledge Graph tooling** — markdown memory (`ats/*/`, `kb/GRAPH.md`) projected into
  `kb/graph.json`, exposed to agents as a queryable tool so nobody re-reads 30+ files.
- **Custom OpenCode configuration** — the 12 portal subagents, permission guardrails,
  and the model/task routing that holds parallel runs together.

## Leash it before you trust it

Left unsupervised, an OpenCode agent with a browser and a shell will wander: re-snapshot
the same page dozens of times, install packages into your system Python, "fix" files you
never asked about, and incinerate half a million tokens doing a 20k-token job. Assume
every agent is one vague instruction away from redecorating your workspace.

So constrain it in `opencode.json` (see `.opencode/opencode.json`) — permissions are
load-bearing, not decorative:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "edit": "ask",
    "bash": { "*": "ask", "uv *": "allow", "node image_slicing.js *": "allow" },
    "external_directory": "deny"
  }
}
```

And per agent in `.opencode/agents/*`: `task: deny` (agents spawning agents is how you
get exponential chaos), `question: allow` for true blockers only, bash limited to
`uv *` / `node *`. If an agent can't finish inside those walls, narrow the task — never
widen the permissions to accommodate the wandering.

## Architecture

```text
Job discovery ──────── Firecrawl (extract listings first, hand structured work to agents)
Browser automation ─── Playwright MCP (accessibility tree, deterministic, stateful)
Existing browser state  Playwright MCP browser extension (real Chrome: sessions, cookies)
Parallelization ────── Portal-specific subagents (.opencode/agents/*, one per ATS)
Long-term knowledge ── Knowledge graph (kb/graph.json) + per-ATS notes (ats/*/)
Orchestration ──────── OpenCode (primary agent plans, subagents execute, ledger checkpoints)
```

The expensive insight: a single naive application run can burn ~500k tokens. Three
decisions keep it cheap — extract before driving (Firecrawl), split by portal
(subagents carry only their ATS context), and query memory instead of re-reading it
(graph lookup instead of 30+ markdown files in context).

## The two drivers

| Driver | Entrypoint | When |
|---|---|---|
| Firecrawl cloud | `apply_orchestrator.py` (multi-tenant), `apply_session.py` (single job) | Scripted runs, credit-budgeted sessions |
| Local Playwright MCP | `initiate_fill.md` + `AGENTS_playwright_cli_optimized.md` | Interactive fills, login-walled flows, form builders |

Both share the same guards (`guards.py`), answer bank (`user_profile.json`,
`work_ex_details.md`), and resume set (`Resumes/`).

## Subagents (`.opencode/agents/`)

One agent per application portal, each a `<name>.md` definition plus a `<name>/AGENTS.md`
playbook. Route strictly by URL fingerprint; never force a fill agent onto the wrong ATS.

| Agent | Portal |
|---|---|
| `job-intel` | Research only — fetches JDs, fingerprints ATS, scores fit, maps resume variant, returns dossiers. Run **before** any fill agent. |
| `workday-fill` | `*.myworkdayjobs.com` |
| `successfactors-fill` | `*.successfactors.com`, TalentBrew `careers.<co>.com/job/*` |
| `avature-fill` | `jobs.<co>.com/Careers/*` |
| `eightfold-fill` | `careers.<co>.com` PCS, `*.eightfold.ai` |
| `greenhouse-fill` | `job-boards.greenhouse.io` |
| `lever-fill` | `*.lever.co` |
| `ashby-fill` | `jobs.ashby.com` |
| `wellfound-fill` | `wellfound.com/jobs/*` |
| `indeed-fill` | `in.indeed.com` |
| `form-fill` | `docs.google.com/forms`, `forms.cloud.microsoft` |
| `profile-fill` | Profile/account pages (never a submitter) |

Each agent: `mode: subagent`, low temperature, capped steps, least-privilege permissions
(no child tasks, questions only when truly blocked), and a distilled-output contract —
insight + `file:line` anchors, never raw dumps.

> `initiate_fill.md` is tried and tested — and so is every agent. Tweak them freely:
> adjust the fill loop, add your own portals, change answer banks and guardrails to fit
> your profile. The invocation list (`@general`, `@job-intel`, `@<portal>-fill`) lives
> at the bottom of `initiate_fill.md`.

## Guards (`guards.py`, projected from `kb/graph.json`)

Every guard exists because a run paid for it (pitfalls in `kb/GRAPH.md`):

- **G1 submit boundary** — automation never clicks Submit/Apply/Send. Unknown terminal
  step = every continue is destructive and blocked. `ALLOW_SUBMIT=1` is human-only.
- **G2 upload integrity** — verify `%PDF` magic + exact byte count *inside* the sandbox
  (an HTML error page named `resume.pdf` is why).
- **G5 no blocking mid-session** — queue questions, report at the end; sessions bill by
  wall-clock and expire (~10 min idle).
- **G7 option resolver** — never type into a dropdown; fuzzy-match ≥ 0.72 or queue.
- **G12 one writer per browser profile** — concurrent agents need separate profiles.
- Plus: honeypot detection, attestation gating, error harvesting (`innerText` lines
  starting `Error`), sponsorship-semantics checks, resume/profile consistency pre-flight.

## Knowledge layers

- `kb/graph.json` — the only source of truth code reads (selectors, answers,
  constraints, terminal steps). Project per tenant: `uv run python kb/project.py <tenant>`.
- `ats/<product>/` — hand-written prose memory (flow shape, quirks, traps). Never read
  by code, never skipped by agents.
- `user_profile.json` > `work_ex_details.md` > resume — the data hierarchy. The resume
  PDF is expected to lag the work history; never filter roles down to resume mentions.

## Setup

- Python via `uv` only (`uv run`, `uv pip install`). Never raw `pip`/`python`.
- Node via `npm run <script>` / `npx`; check `package.json` first
  (`@mendable/firecrawl-js`, `dotenv`, `sharp`).
- `.env` holds `FIRECRAWL_API_KEY`; Firecrawl CLI on PATH; browser work via Playwright MCP.
- Portal login rule: enter email only and pause — the human supplies passwords/OTPs.
  Never invent credentials.

## Commands

```powershell
# tests — the real suite (run from repo root)
uv run pytest testing_files/test_guards.py -q
uv run pytest testing_files/test_guards.py -q -k terminal_step

# pre-flight (no credits, no session)
uv run python preflight.py
uv run python preflight.py --warn-only --no-probe

# Firecrawl cloud — single job / orchestrator
uv run python apply_session.py --job HPE --dry-run
$env:JOB="HPE"; $env:DRY_RUN="1"; uv run python apply_orchestrator.py
firecrawl credit-usage --json

# local Playwright MCP — read initiate_fill.md first
```

Budget: cap 150 credits/run, abort if < 200 remain. Always stop cloud sessions, even on
failure — leaked sessions keep billing.

## Ledgers & checkpoints

`jobs_applied.json`, `wellfound_progress.json`, `ats_progress.json`, `job_links.json`
(note: `job_links.json` has no outer braces by design — don't "fix" it),
`*_submit_authority.json` (human-granted, required before any final click).
Checkpoint every 2–3 applications.

## Gotchas that will cost a run

- Workday: errors only via `innerText`; `data-automation-id` on wrappers; searchable
  prompts need `promptSearchButton` → Search → Enter; LinkedIn URLs need `www.`;
  Role Description bans `< > [ ] { } " \``.
- Phenom: element IDs contain dots/spaces — use `[id='…']`, never `#id`.
- Playwright refs go stale after any DOM change — snapshot → act → re-snapshot.
- `interact --python -c` runs only the first statement; prompts are the only mode that
  both acts and reports.
- Verify before claiming success: targeted edit → `uv run pytest
  testing_files/test_guards.py -q` (+ `ruff check` if available). No clean evidence, no success.
