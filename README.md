# Job-Application Automation Harness

Fill job applications with AI agents — cheaply, in parallel, without losing the plot.
One posting = one form session. The automation fills everything safely answerable and
stops on the review page. **The final Submit always belongs to a human** (unless an
explicit per-portal `*_submit_authority.json` is granted).

Built on [OpenCode](https://opencode.ai) orchestration, dual Playwright MCP drivers
(isolated profile + live Chrome extension), SerpApi Google dorking, Firecrawl extraction,
16 specialized subagents, automated PDF cover letter generation, and per-ATS memory
capturing the lessons each run teaches.

## Quickstart (the easy way)

```bash
git clone <this-repo> && cd <this-repo>
opencode            # install it first if you haven't: https://opencode.ai
```

Then in the session, launch a fill with:

```text
@initiate_fill.md <paste the job link here>
```

That's it — the prompt routes to background recon (`job-intel`), generates a tailored
cover letter or short answer if needed (`cover_letter_agent` / `answer-writer`), and
dispatches the matching portal subagent, which fills the application and pauses on the
review page for your Submit.

## Skills, Tools & Plugins that quietly balance it all

- **Dual Playwright MCP (`playwright` & `playwright-extention`)** — stateful,
  accessibility-tree-driven browser automation via both a dedicated Chrome user profile
  and the Playwright MCP Chrome extension (attaching directly to your real logged-in
  browser tabs for session-heavy portals like Instahyre, Wellfound, and Hirist).
- **Playwright Context Prune (`.opencode/plugins/strip-playwright-results.ts`)** — an
  OpenCode chat-transform plugin that automatically strips stale Playwright accessibility
  trees from earlier turns, keeping only the latest completed browser output so multi-step
  fills never blow up the context window.
- **Google Search Dorking Tool (`.opencode/tools/google_search.ts`)** — SerpApi-backed
  first-preference search tool supporting exact dork operators (`site:`, `intitle:`,
  `after:`), paired with `src/search_guidance/search_hack.md` and
  `ai_ml_data_job_dorking_playbook.md` to surface fresh India/Remote AI/ML/SDE fresher roles.
- **Headroom Proxy & GraphRAG** — local proxy (`headroom`) plus Neo4j knowledge graph
  (`src/scripts/graph_rag.py`) to keep context lean while keeping every ATS quirk on tap.
- **Cover Letter & Pitch Engine** — instant customized PDF generation
  (`src/scripts/generate_cover_letter.py` via `markdown-pdf`) and curated answer banks
  (`src/knowledge_source/submission_pitch.md` and `wellfound_interest_answer.md`).
- **Task Observer** — monitors multi-step runs for reusable workflow patterns worth
  preserving as skills.

## Leash it before you trust it

Left unsupervised, an agent with a browser and a shell will wander: re-snapshot the same
page dozens of times, read `.env` secrets or old run logs, and burn half a million tokens
doing a 20k-token job.

So constrain it in `.opencode/opencode.json` — permissions and context guards are
load-bearing, not decorative:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "subagent_depth": 2,
  "permission": {
    "*": "allow",
    "bash": {
      "*": "allow",
      "git config --global user.name *": "ask",
      "git config --global user.email *": "ask"
    },
    "read": {
      "*": "allow",
      "*.env": "deny",
      "*.env.*": "deny",
      "*.pem": "deny",
      "*.key": "deny",
      "**/secrets/**": "deny",
      "*/runs/**": "deny",
      "**/opencode.json": "deny"
    },
    "edit": {
      "*": "allow",
      "*.env": "deny",
      "*.env.*": "deny",
      "*.pem": "deny",
      "*.key": "deny",
      "**/secrets/**": "deny",
      "../**": "deny",
      "*/runs/**": "deny",
      "**/opencode.json": "deny"
    },
    "external_directory": "deny"
  }
}
```

And per agent in `.opencode/agents/*`: `task: deny` (subagents never spawn child
subagents), `question: allow` for true blockers only, and strict read/edit/bash
allowlists tailored to each agent's exact job.

## Architecture

```text
Job discovery ───────── google_search tool (SerpApi dorking) + Firecrawl extraction
Browser automation ──── Playwright MCP (local profile) + Playwright Extension MCP (live Chrome)
Context pruning ─────── strip-playwright-results.ts plugin + Headroom proxy + Neo4j GraphRAG
Parallelization ─────── 16 specialized subagents (.opencode/agents/*) + general/explore/scout
Answer & pitch engine ─ submission_pitch.md + wellfound_interest_answer.md + cover_letter_agent
Long-term knowledge ─── per-ATS notes (ats/*/) + platform bottlenecks (src/knowledge_source/*)
Orchestration ───────── OpenCode (multi-tab management, batch submit gating, JSON ledgers)
```

### Multi-Tab & Multi-Agent Rules
- **One tab per application:** Multi-job agents open each application in a separate tab,
  switch deterministically by tab index, and fill **one application at a time**.
- **Human submit gate & tab cleanup:** When a batch of applications reaches the review
  step, the orchestrator pauses to ask the user to submit or grant submit authority, then
  closes completed tabs to keep browser state clean.
- **Role filtering:** Automatically skips roles requiring 2+ years of experience ("Senior"
  titles), non-India roles (unless Remote), and non-Python primary stacks (e.g., pure
  Java/C++ roles without Python).

## The Drivers

| Driver | Entrypoint | When |
|---|---|---|
| **Local Playwright MCP** (Primary) | `initiate_fill.md` + `src/scripts/page_recon.js` + `src/scripts/image_slicing.js` | Standard ATS fills (`RECON ONCE → DECIDE ONCE → ACT IN BATCHES → VERIFY ONCE`) |
| **Playwright Extension MCP** | `src/knowledge_source/job-application-roadmap_wellfound_instahyre.md` | Logged-in Chrome flows (Instahyre apply-all sweeps, Wellfound, Hirist, Naukri) |
| **Firecrawl Cloud** (Secondary) | `src/scripts/apply_orchestrator.py` (multi-tenant), `src/scripts/apply_session.py` (single job) | Scripted cloud runs, credit-budgeted sessions |

All drivers share the same guards (`src/scripts/guards.py`, `guards.json`), profile truth
(`user_profile.json` > `work_ex_details.md`), answer banks (`src/knowledge_source/`), and
resume variants (`Resumes/`).

## Subagents (`.opencode/agents/`)

16 specialized subagents live in `.opencode/agents/`, each with a `<name>.md` definition
and a `<name>/AGENTS.md` playbook. Route strictly by URL/ATS fingerprint or task type —
never force a fill agent onto the wrong portal.

| Agent | Role / Target Portal |
|---|---|
| `job-intel` | **Research only** — fetches JDs, fingerprints ATS, scores fit vs `work_ex_details.md`, maps resume variant (`GenAI_DS` / `ML_Vision` / `ML_Vision_RL`), returns dossiers. Run **before** any fill agent. |
| `workday-fill` | `*.myworkdayjobs.com` (WD1 / WD5 / EXT multi-step wizards) |
| `successfactors-fill` | `*.successfactors.com` + TalentBrew `careers.<co>.com/job/*` |
| `avature-fill` | `jobs.<co>.com/Careers/*` (`/JobDetail` → `ApplicationMethods` → `Register`) |
| `eightfold-fill` | `careers.<co>.com` PCS / `*.eightfold.ai` (`/careers/job/<pid>` → `/careers/apply`) |
| `greenhouse-fill` | `job-boards.greenhouse.io/<org>/jobs/<id>` (single long page) |
| `lever-fill` | `*.lever.co` (single long page; detects off-board `EXTERNAL_FLOW` redirects) |
| `ashby-fill` | `jobs.ashby.com/<org>/<slug>` (single long page) |
| `wellfound-fill` | `wellfound.com/jobs/*` (fast modal/page fill with tailored interest answers) |
| `indeed-fill` | `in.indeed.com` search + `Apply with Indeed` / `Easily apply` flows |
| `hirist-fill` | `hirist.tech` (API-first flow via `browser_evaluate`, one-click apply authority check, assessment parking) |
| `instahyre-apply-all` | `instahyre.com/candidate/opportunities` (unlimited high-speed apply-all sweep over extension MCP, frozen `years=2`, skill cycling, bulk toast verification) |
| `form-fill` | Single-page form builders: `docs.google.com/forms` & `forms.cloud.microsoft` |
| `profile-fill` | Candidate profile/account pages (`my.greenhouse.io/profile`, `workatastartup.com`, Weekday, Hirist, Naukri). Stages profile data; never submits job applications. |
| `answer-writer` | Generates human-style short answers (≤100 words) for *"Why this company?"* / *"Why are you a good fit?"* using `Resumes/cover_letter.md`, `work_ex_details.md`, the JD, and at most one `websearch`. |
| `cover_letter_agent` | Fast customized cover letter PDF generator. Runs `src/scripts/generate_cover_letter.py` on `Resumes/cover_letter.md` to output `Resumes/cover_letter/cover_letter_<company>.pdf`. |

Built-in orchestration subagents (`general` for parallel multi-step execution, `explore`
for read-only codebase lookups, `scout` for external dependency docs) keep the primary
agent's context window clean.

## Repository Structure

```text
├── .opencode/
│   ├── agents/                 # 16 subagent definitions (*.md) + playbooks (*/AGENTS.md)
│   ├── plugins/                # strip-playwright-results.ts (context pruning)
│   ├── tools/                  # google_search.ts (SerpApi dorking)
│   └── opencode.json           # MCP servers, Headroom provider, permission guardrails
├── ats/                        # Per-ATS prose memory (18+ portals: workday, ashby, lever, etc.)
├── Resumes/
│   ├── cover_letter.md         # Master cover letter markdown template
│   ├── cover_letter/           # Generated company-specific PDFs (cover_letter_<company>.pdf)
│   └── *.pdf                   # Resume variants (GenAI_DS, ML_Vision, ML_Vision_RL)
├── src/
│   ├── accessability_snapshot/ # Saved company accessibility snapshots
│   ├── application_progress/   # Session summary reports (applied, skipped, parked)
│   ├── applied/                # Platform-specific applied ledgers with timestamps
│   ├── internship_appli_fill/  # Internship-specific fill rules
│   ├── job_search_results/     # Harvested & queued fresher job postings
│   ├── knowledge_source/       # submission_pitch.md, wellfound_interest_answer.md,
│   │                           # job-application-roadmap_wellfound_instahyre.md, <portal>/bottlenecks.md
│   ├── scripts/                # All Python & JS scripts (generate_cover_letter.py, guards.py,
│   │                           # page_recon.js, image_slicing.js, graph_rag.py, preflight.py, etc.)
│   ├── search_guidance/        # search_hack.md (Google dork templates & query banks)
│   └── submit_permisssions/    # Human-granted *_submit_authority.json files per platform
├── test/                       # Pytest suites (test_guards.py, KG_testing.py, testing.py)
├── AGENTS.md                   # Global agent rules, routing, delegation, and file hygiene
└── initiate_fill.md            # Master Playwright MCP fill loop prompt
```

## Knowledge Layers & Answer Banks

- **Data hierarchy:** `user_profile.json` > `work_ex_details.md` (authoritative work
  history) > resume PDFs (`Resumes/`). Never filter work history down to resume mentions.
- **Master Candidate Pitch (`src/knowledge_source/submission_pitch.md`):** Single unified
  answer used across all agents for broad prompts (*"tell me what you have done"*,
  *"what all projects have you worked on"*, *"your ML journey"*, *"what makes you
  special"*). Covers IIT Kharagpur B.Tech research under Prof. Pabitra Mitra, 3 shipped
  production agentic systems (Pascal AI Labs `DFR-Tracer`, Pibit.AI `Template Mapper` &
  `Global PDF Handler`, CJBS workflow), ML pipelines at Symx AI and Innovaccer, Kaggle
  Expert (Rank 3911, top 7%), Snowflake AI Hackathon Winner, Amex Decision Science 2nd
  Runner-Up, and open-source work (`Agentic-Commerce`).
- **Company Interest Bank (`src/knowledge_source/wellfound/wellfound_interest_answer.md`):**
  Domain-mapped answer templates and project deep-dives tailored to GenAI/Agents,
  CV/Multimodal, and RL/Decision Science roles.
- **Custom Cover Letter Generator (`src/scripts/generate_cover_letter.py`):** Compiles
  `Resumes/cover_letter.md` into `Resumes/cover_letter/cover_letter_<company>.pdf` via
  `markdown-pdf`, automatically capitalizing the company name in the salutation
  (`Dear GOOGLE Hiring Team,`), injecting the target role and company into the opening
  and closing paragraphs, and handling file locks gracefully.
- **Per-ATS Memory (`ats/<product>/`) & Bottlenecks (`src/knowledge_source/<portal>/bottlenecks.md`):**
  Hand-written notes capturing flow shapes, widget quirks, and persistent blockers (logged
  when an issue recurs 3+ iterations).

## Guards (`src/scripts/guards.py`, rules in `guards.json`)

Every guard exists because a run paid for it:

- **G1 submit boundary** — automation never clicks Submit/Apply/Send without explicit
  human authority (`src/submit_permisssions/*_submit_authority.json` or `ALLOW_SUBMIT=1`).
- **G2 upload integrity** — verify `%PDF` magic bytes + exact byte count before upload.
- **G5 no blocking mid-session** — queue unknown non-blocking questions and report once at
  the end.
- **G7 option resolver** — never type blindly into a dropdown; enumerate options and
  fuzzy-match ≥ 0.72 or queue.
- **G12 one writer per browser profile** — concurrent agents use separate tabs/profiles.
- Plus: honeypot detection, attestation gating, error harvesting (`innerText` lines
  starting `Error`), sponsorship-semantics checks, and resume/profile consistency pre-flight.

## Graph Memory (`src/scripts/graph_rag.py`)

To prevent context bloat from dozens of markdown playbooks, notes are indexed into a
**Neo4j knowledge graph** (`src/scripts/markdown_to_neo4j_gemini.py` &
`src/scripts/graph_rag.py`), allowing agents to query targeted entity/relationship slices
with a safe local markdown fallback when Neo4j is offline.

## Setup

- Python via `uv` only (`uv run`, `uv pip install`). Never raw `pip`.
- Node via `npm` / `npx` (`@mendable/firecrawl-js`, `dotenv`, `sharp`, `serpapi`).
- `.env` keys:
  - `SERPAPI_API_KEY` — powers `.opencode/tools/google_search.ts` for Google dorking.
  - `FIRECRAWL_API_KEY` — powers Firecrawl discovery and cloud sessions.
  - `PLAYWRIGHT_MCP_EXTENSION_TOKEN` — connects `playwright-extention` MCP to your live Chrome.
- Portal login rule: enter email only and pause — the human supplies passwords/OTPs.
  Never invent credentials.

## Commands

```powershell
# Generate a customized cover letter PDF
.venv\Scripts\python.exe src\scripts\generate_cover_letter.py "Google" "AI/ML Engineer"
uv run python src/scripts/generate_cover_letter.py --company "Anthropic" --role "Research Engineer"

# Run guard & knowledge-graph test suites
uv run pytest test/test_guards.py -q
uv run pytest test/test_guards.py -q -k terminal_step
uv run pytest test/KG_testing.py -q

# Pre-flight checks (no credits, no session)
uv run python src/scripts/preflight.py
uv run python src/scripts/preflight.py --warn-only --no-probe

# Firecrawl cloud — single job / orchestrator
uv run python src/scripts/apply_session.py --job HPE --dry-run
$env:JOB="HPE"; $env:DRY_RUN="1"; uv run python src/scripts/apply_orchestrator.py
firecrawl credit-usage --json

# Local Playwright MCP — read initiate_fill.md first
```

## Ledgers & Checkpoints

- **Applied jobs:** `src/applied/jobs_applied.json` and platform-specific ledgers in
  `src/applied/` (appended with exact `date-time`).
- **Search & queues:** `src/job_search_results/` (marked as applied once completed).
- **Session summaries:** `src/application_progress/`.
- **Submit permissions:** `src/submit_permisssions/*_submit_authority.json` (human-granted
  authority required before any final submit click).
- Checkpoint ledgers every 2–3 applications.

## Gotchas that will cost a run

- **Workday:** errors only via `innerText`; `data-automation-id` on wrappers; searchable
  prompts need `promptSearchButton` → Search → Enter; LinkedIn URLs need `www.`;
  Role Description bans `< > [ ] { } " \``.
- **Hirist:** detail pages don't reliably hydrate via direct navigation; use API-first
  flow via `browser_evaluate` and treat Apply as a one-click final submit.
- **Instahyre:** keep `company_size=0&job_type=0&search=true&years=2` frozen in the
  opportunities URL; if redirected to `?matching=true`, switch to the UI search flow
  rather than looping redirects.
- **Phenom:** element IDs contain dots/spaces — use `[id='…']`, never `#id`.
- **Playwright refs:** refs go stale after any DOM change — reuse the snapshot returned by
  each MCP action, and re-snapshot only on navigation, modal open, or stale-ref error.
- **Long prose (>200 chars):** base64-encode and set via `browser_evaluate` using the
  native HTMLTextAreaElement/HTMLInputElement value setter + `input`/`change` events so
  characters aren't dropped in transit.

## Useful References

- [Playwright MCP](https://github.com/microsoft/playwright-mcp) — MCP server setup,
  browser profiles, extension mode, and tool reference for `initiate_fill.md`.
- [OpenCode Agents Docs](https://opencode.ai/docs/agents/) — agent configuration,
  permissions, and subagent routing.
- [Firecrawl Introduction](https://docs.firecrawl.dev/introduction) — scrape / search /
  extract overview behind discovery and cloud sessions.
- [markdown-pdf](https://pypi.org/project/markdown-pdf/) — PDF rendering engine used by
  `src/scripts/generate_cover_letter.py`.
