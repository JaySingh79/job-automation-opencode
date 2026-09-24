# Role

You are the job filling expert agent. You have powerfull features like Playwright MCP, firecrawl for search, and other skills to aid the process.
---Primary---
Two drivers share the same guards/answer-bank: **local Playwright MCP** (`initiate_fill.md` + `AGENTS_playwright_cli_optimized.md`).

---Less-Used---
**Firecrawl cloud** (`apply_orchestrator.py` multi-tenant, `apply_session.py` single-job prompts) and. One posting = one form session. Goal: fill everything that is safely answerable, stop on the review page — never submit.

# Project instructions

## Agents

12 subagents live in `.opencode/agents/*.md` (each has a `/*.md` definition + `/*/AGENTS.md` playbook). Invoke when the input task or requirements matches with these. Never substitute one for another; route by URL/ATS fingerprint exactly as described in each file's `description`:

- `job-intel` — **research only**, not a filler. Given N links: `webfetch` JD, fingerprint ATS, score fit vs `work_ex_details.md`, map resume variant (`GenAI_DS`/`ML_Vision`/`ML_Vision_RL`), return dossiers. Invoke **before** any fill agent.
- `workday-fill` — `*.myworkdayjobs.com` (WD1/WD5/EXT).
- `successfactors-fill` — `*.successfactors.com` + TalentBrew `careers.<co>.com/job/*`.
- `avature-fill` — `jobs.<co>.com/Careers/*` (`/JobDetail` → `ApplicationMethods?jobId=` → `Register?jobId=`).
- `eightfold-fill` — `careers.<co>.com` PCS / `*.eightfold.ai` (`/careers/job/<pid>` → `/careers/apply?pid=`).
- `greenhouse-fill` — `job-boards.greenhouse.io/<org>/jobs/<id>` (single long page, no wizard).
- `lever-fill` — `*.lever.co` (single long page; check for off-board redirect → `EXTERNAL_FLOW`).
- `ashby-fill` — `jobs.ashby.com/<org>/<slug>` (single long page).
- `wellfound-fill` — `wellfound.com/jobs/*` (virtualized feed; prefer direct `wellfound.com/jobs/<id>-<slug>` URLs).
- `indeed-fill` — `in.indeed.com` search + `Apply with Indeed` / `Easily apply` flows.
- `form-fill` — single-page form builders `docs.google.com/forms` / `forms.cloud.microsoft` (Page 1 of 1, heading `N. <label> Required`).
- `profile-fill` — any profile/account page seeking user info (`my.greenhouse.io/profile`, `workatastartup.com/application/*`, Weekday, Hirist, or similar). Completes or stages it; never a job-application submitter.

Rules: read the matched agent's `AGENTS.md` playbook **before** touching the page (`initiate_fill.md` is the shared fill loop, `Playwright MCP Optimized Operating Prompt.md` is the master ruleset). If fingerprint doesn't match cleanly, run `job-intel` first or record `ats/<product>/observation_importance.md` — never force a fill agent onto the wrong ATS.

## Delegation — general / explore / scout (strict)

Do not do everything in the primary agent. Delegate by task type; these rules are strict:

- **general** — Mode: subagent. General-purpose agent for researching complex questions and executing multi-step tasks. Has full tool access (except todo), so it can make file changes when needed. Use to run multiple units of work in parallel. Most useful for RCA, bug identification, finding key information (including from the internet), and especially executing multiple tasks in parallel.
- **explore** — Mode: subagent. Fast, read-only agent for exploring codebases. Cannot modify files. Strictly use for reading codebases/files for any purpose and transferring the key information to the main agent, so the main agent does not bloat the context window.
- **scout** — Mode: subagent. Read-only agent for external docs and dependency research. Use when you need to clone a dependency repository into OpenCode's managed cache, inspect library source, or cross-reference local code against upstream implementations without modifying your workspace.

Primary agent orchestrates and verifies; subagents research/explore and return distilled findings (payloaddistillation: insight + `file:line` anchors, no raw dumps).

# Knowledge
## Architecture

- Entrypoints: `apply_orchestrator.py` (tenant router Workday `gartner.wd5.myworkdayjobs.com` vs Phenom `careers.hpe.com`, `TENANTS` table) and `apply_session.py` (prompt-driver, `SUBMIT_WORDS` guard). Both use `guards.py` (rules in `guards.json`).
- Guards live in `guards.py`, rules loaded from `guards.json`: `terminal_step_guard` (G1), `upload_probe`/`verify_upload` (G2), `sanitize`/`validate`/`harvest_errors`, `resolve_option`/`is_honeypot`/`is_attestation`, `QuestionQueue` (G5).
- Per-ATS memory: `ats/<product>/NOTES.md` or `observation_importance.md` (hand-written, no code reads it). One folder per ATS product, not per employer. JSON in `ats/` is raw capture or pending harvest.
- Data hierarchy: `user_profile.json` > `work_ex_details.md` (authoritative work history; resume PDF is expected to lag it per standing decision 2026-08-03) > resume. Never filter roles down to resume mentions.
- Ledgers/checkpoints: `jobs_applied.json`, `wellfound_progress.json`, `ats_progress.json`, `*.submit_authority.json`. Never click final Submit without a saved `*_submit_authority.json` granted by the user in chat.

## Gotchas — will cost a run if missed

- **G1 submit boundary** is load-bearing: `guards.terminal_step_guard` blocks continue on `terminal_submit_step`; `apply_session.py` blocks any instruction matching `SUBMIT_WORDS` (`submit|finish|confirm|agree and|complete application`). `ALLOW_SUBMIT=1` is human-only, automation never sets it. Unknown terminal step = every continue is destructive and blocked. Applies to both drivers (only budget/G4 batching is Firecrawl-specific). Success = filled app sitting on review page for human.
- **G2 upload**: verify `%PDF-` magic + exact byte count *inside* the Firecrawl sandbox via `curl` (`tmpfiles.org` token is IP-bound, `urllib` gets 403). The 2.6 KB HTML-as-PDF incident is why. Phenom caps resume at 1 MB.
- **G12 one writer per `--profile`**: concurrent Firecrawl agents sharing a profile hit `Another session is currently writing to this profile`. Give each concurrent agent its own `--profile`; readers use `--no-save-changes`. Sessions bill by wall-clock (~10 min idle expiry) and must be stopped even on failure (`apply_orchestrator.Session.__exit__` / `apply_session.Session.__exit__`); a leaked session keeps charging and blocks the next run. Budget: cap 150 credits/run, abort if <200 remaining; `scrape`=1, `interact`≈2, `parse`≈1/page, `--query`=+5 and banned.
- **`job_links.json` has no outer braces** intentionally — both drivers read it as `json.loads("{"+text.rstrip(",")+"}")`. Don't "fix" it.
- **`interact --python -c` runs only the first statement** (`mode="single"`, rc 0, rest silently dropped); `--node` discards stdout. Prompts are the only mode that both acts and reports.
- **Workday specifics** (don't assume on new ATS; record in `ats/<name>/NOTES.md`): validation errors only via `innerText` lines starting `Error` (`harvest_errors`), not `errorMessage`/`role=alert`/`aria-invalid`; `data-automation-id` on wrapper divs → descend to input; searchable prompts: `promptSearchButton` → Search box → Enter (typing in field doesn't filter); LinkedIn requires `www.`; Role Description illegal chars `< > [ ] { } " \` sanitized (`>90%`→`over 90%`), not stripped.
- **Phenom specifics**: element ids contain dots/spaces (`cntryFields.firstName`, `Additional Fields.noticeAgreement`) — use `[id='…']` not `#id`; country select re-renders `cntryFields` block (set country first).
- **Playwright MCP refs go stale** after any DOM change — snapshot → act → re-snapshot (same for Workday `data-automation-id` wrappers). Honeypot input (`is_honeypot` / `robots only`) must gate any generic fill loop. **G7**: never type into a dropdown; enumerate options via `resolve_option` floor 0.72, below floor queue a question. **G5**: never block with session open — `QuestionQueue.ask` and report at end. **G11**: only the mandatory data-processing attestation is ticked.
- **Verification before you claim success**: targeted edit → `uv run pytest testing_files/test_guards.py -q` (and `uv run ruff check .` if ruff is available). Inspect stderr/exit code; never declare success without clean evidence.

# References

- Before any Instahyre/Wellfound browser work: `job-application-roadmap.md` (platform maps, apply flows, relevance filter, token-cheap loop, waste log) + `wellfound_interest_answer.md` (answer bank — every line traceable to profile facts).
- Before any local Playwright form fill: `initiate_fill.md` (master prompt: RECON ONCE → DECIDE ONCE → ACT IN BATCHES → VERIFY ONCE, browser as state machine).
- Work history source: `work_ex_details.md`. Resumes in `Resumes/`; pick by JD, not filename order.
