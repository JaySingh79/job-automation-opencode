# wellfound-fill — AGENTS.md

Platform playbook for the `wellfound-fill` subagent. Read this before touching any
Wellfound page (`wellfound.com/jobs*`). Shared fill loop: `initiate_fill.md`.
Roadmap: `job-application-roadmap.md`.
Job types: `AI/ML/SDE/Data Science/AI Product`

## Instruction
- `STRICTLY no other files to be read` apart from File_Guide. Every information about my candidature is already in Wellfound. Just apply.
- *Expected CTC* : `22 LPA (18+4)`
- *Pay Range* : `22-26 LPA (negotiable)`
- 
### File_Guide
Only files you should read before starting.
- @initiate_fill.md
- @src\knowledge_source\wellfound\wellfound_interest_answer.md
- @src\knowledge_source\job-application-roadmap_wellfound_instahyre.md

### 1. Fingerprint

- Login: `https://wellfound.com/login` Mostly the browser has the previous login session token so login issue won't occur.
  If still asked for login:
    Email + Password + `Log in`, plus `Continue with
    Google`. Credentials live in `user_profile.json → credentials.wellfound`. Fill known email
    freely; confirm password use with the human per `initiate_fill.md`, then batch-fill both
    fields in ONE `browser_fill_form` and click `Log in`.
- Jobs feed (`/jobs`, logged in): saved-search chips (e.g. Data Scientist / ML / AI),
  Asia/location menu, `Filters`, `<N> results` heading (drops as you apply), the notice
  `Hiding jobs that do not accept applications from your location`, per-card Save / Learn
  more / Remove / Hide / Report. `Remove` = already saved. The list is virtualized (~28 job
  links in DOM max) — do NOT scroll-loop expecting pagination. Harvest IDs from cards AND
  from `Similar jobs` sections on detail pages instead.
- Prefer direct job URLs `https://wellfound.com/jobs/<id>-<slug>` — standalone detail pages,
  ~200-token evaluate recon, no 10–15k list snapshots.
- Global `/search` (Search everything box) does NOT search jobs (`0 results`) — dead end,
  never type into it.

### 2. Token-cheap per-job loop (validated 2026-10-11 — follow EXACTLY, see §8)

1. `tabs new` → direct job URL (fresh tab per job; browser auto-prunes old tabs).
2. ONE `evaluate` recon: exp line, salary, ext-flow markers (`apply at|email|send resume|careers@`),
   Apply vs `✓ Applied` BUTTON texts (never page innerText — nav `Applied` tab false-positives),
   first ~400 chars of head.
   - FAST 1-SECOND BAILOUT & EXCLUSION (ZERO TIME WASTE): If ANY of the following match:
     a) Already Applied (✓ Applied button disabled)
     b) Job posting no longer available / closed / expired / 404 ('This job has closed', 'The job listing is no longer available', etc.)
     c) Experience requirement > 3 years (>3 YoE)
     d) Location beyond India (outside India and not remote-eligible)
     e) Job posting date MORE THAN 2 MONTHS OLD (e.g. 'POSTED 2 MONTHS AGO', 'POSTED 3+ MONTHS AGO', or 'YEARS AGO')
     -> Close tab immediately within <= 1s (	abs(close)), record reason, and proceed to next job immediately without wasting any time, snapshots, or modal clicks. SKIP HERE on filter fail — never snapshot, never find.
3. ONE synthetic Apply click via `evaluate`
   (`Array.from(document.querySelectorAll('button')).find(x => x.innerText.trim() === 'Apply').click()`).
   NEVER trusted `click` on Apply — always times out (`element never stable` / overlay intercepts).
4. `wait_for time:3` → `find` for `What interests|Send application`. If absent → ONE reload
   (`navigate` same URL) + ONE synthetic reclick + `wait_for time:5` + `find` again. Still absent →
   record BLOCKED_MODAL_LOAD, next job. (Modal fetch hangs are the only legal waits; §7 no-wait rule
   is suspended for modal-load only.)
5. `fill_form` the interest box (Variant A default, B ML-systems, C high-stakes, D junior) →
   ONE synthetic Send click via `evaluate`
   (`document.querySelector('[data-test="JobApplicationModal--SubmitButton"]').click()`).
   NEVER trusted `click` on Send — same timeout.
6. `evaluate` button-text check for `✓ Applied` (disabled). Report evidence in return payload only.
   No file saves of any kind, ever — no checkpoints, no ledgers, no count updates. The only
   instruction is to keep applying to jobs without stop.
7. Only use the `answer-writer` sub agent when the role and `wellfound_interest_answer.md` don't coiencide.

### 3. Apply modal variants

- (a) single `What interests you about working for this company?` textbox.
- (b) `Write a note to <company>.` textbox.
- (c) conditional radios: location `I can relocate to…` + autocomplete, US-hours overlap,
  LLM-API Yes/No gating a follow-up textbox. Disabled textbox → resolve the dependency
  FIRST: click radio (via `input[value=relocate_to]` evaluate when the a11y ref is missing)
  → `type` city `slowly:true` → click the exact suggestion → textbox enables, Send enables.
- Hard block: `"<Company> is not accepting applications from your current location…"`
  disables ALL inputs + Send. Do NOT retry — Cancel, continue to next job immediately.
- Soft warning: `You're outside the years of experience preferred (N+ years)` still allows
  Send — allowed under submit authority; profile stays truthful, the company decides.

### 4. Answers (profile-backed only)

- 18mo total experience, Immediate notice, India authorization, sponsorship `No` for India
  roles, *Pay Range*  / numeric `22`. Prose from `work_ex_details.md` only.
- For modal notes asking "tell me what you have done", "what projects have you worked on", "your ML journey", "what makes you special", or candidate overview, strictly use `src/knowledge_source/submission_pitch.md`. For company interest notes ("What interests you about working for this company?"), use `wellfound_interest_answer.md`.
- JD text vs sidebar Experience often disagree — trust the STRICTER one.
- Watch for external-apply instructions inside the JD (`apply at: http://…`, external
  Application Link) → DEFER as EXTERNAL_FLOW, don't treat the Wellfound button as the real
  application (observed: Parsewave, Beyond).
- SKIP : SENIOR_TITLE/5Y_GAP, SALARY_FLOOR(≤10L), VOICE_OR_SECURITY_CORE_GAP, LEVEL_MISMATCH, DOMAIN_OR_INFRA_MISMATCH, EXTERNAL_FLOW. (NOTE: SAME_COMPANY_2ND IS REMOVED - Multiple distinct roles at the same company ARE ALLOWED).
- MULTIPLE ROLES PER COMPANY ALLOWED: If a company has multiple distinct job postings (e.g. AI/ML, Data Science, SDE/Software Engineer, Backend), you CAN and MUST apply to all matching roles at that company. Applying to multiple distinct roles at the same company does NOT violate any rules.
- SDE FRESHER ROLES FULLY TARGETED: Fresher SDE / SWE / Software Engineer / Backend / Python Developer roles (<=2 YoE, or up to 3 yrs) are explicitly welcomed and must be applied to.
- Fill *Expected CTC* salary cap, `expected CTC`, but apply to roles with already mentioned pay even less than 18L.
- Can apply to jobs requiring up to `3yrs of experience` but *NOT* more than 3.

### 5. Verification (no ledgers, no saves)

- Verify via `document.body.innerText` / button-text check for `✓ Applied` (disabled), not
  via re-snapshot. Verify counts drop on the feed (`174 results` heading) as corroboration.
  Report evidence in return payload only.

### 6. Output contract

`RECON → PLAN → FILL → VERIFY` per job, no call narration. Final: filled count, variant
used, `✓ Applied` evidence. Waste-log reminders: no per-field snapshots, no modal-X clicks (navigate resets
modals), no regex literals with `/jobs/` inside evaluate strings (use `indexOf`), no global
search box.

## 7. Non-stop apply-all (2026-10-08, user order no checkpoints)
- *No Checkpoint pause needed, keep applying without stop, without check, until jobs for the search run out, or human says STOP. Never stop until human STOP.*
- *Agents are NOT authorised to pause, hold, park URLs, save status, update files, create checkpoints, or write temporary ledgers. Continuously keep applying.*
- *No holding to update counts, no sheets, no `src/applied/*.json`, no `src/application_progress/*.json`, no snapshot saves unless failure/debug. Report counts and evidence in return payload only, in bulk afterwards.*
- *Do NOT wait for settle/verify before next Apply. Click Apply → Send → next job immediately back-to-back with minimal gaps. Verify in bulk afterwards via `✓ Applied` counts, not per-click blocking waits.*
- *Only hard stops: login/OTP/CAPTCHA block, or explicit user STOP. 3-consecutive-failure rule becomes skip-failing-IDs-and-rotate (skip failing IDs, continue rest), not full stop, not checkpoint-and-pause.*

### 8. Exact call sequence per job (copy this shape — 6 calls apply, 3 calls skip)

Apply path: `tabs(new,url)` → `evaluate(recon)` → `evaluate(synthetic Apply click)` →
`wait_for(3)` → `find(What interests|Send application)` → `fill_form(interest box)` →
`evaluate(synthetic Send click)` → `evaluate(✓ Applied check)`.
Skip path: `tabs(new,url)` → `evaluate(recon)` → next job (2 calls).
Conditional modal (disabled interest box): + `snapshot(target=dialog)` → resolve dependency
(radio click → `type slowly:true` city → click exact suggestion) → box enables → continue.
Poison tab (zombie empty dialog / loading-stuck modal after the 3s+reload cycle): `tabs(close)` +
fresh `tabs(new)` — NEVER re-click Apply/Send in a poisoned tab.
Banned (all validated timeouts, zero exceptions): trusted `click` on Apply or Send buttons,
full `snapshot` before recon verdict, per-field snapshots, modal-X clicks, global search box.
Console ad-block errors (`ERR_BLOCKED_BY_CLIENT`) are noise — ignore unless modal fails twice,
then read console once before recording BLOCKED_MODAL_LOAD.

## 9. Strict rules — 2026-10-14 (user order, no exceptions)
- SDE FRESHER ROLES & MULTIPLE COMPANY POSTINGS (2026-10-26 USER DIRECTIVE):
  1. SDE / SWE / Software Engineer / Backend / Python Developer fresher roles are explicitly welcomed and MUST be applied to.
  2. If a single company has multiple relevant postings (e.g. SDE, AI Engineer, Data Scientist, ML Engineer), APPLY TO ALL OF THEM. Do NOT skip second or third postings at the same company.
- FAST 1-SECOND BAILOUT & EXCLUSION (MANDATORY, ZERO TIME WASTE): Quickly close and exclude within 1 second any application that shows:
  1. Already applied (✓ Applied button disabled)
  2. Job posting no longer available ('This job has closed', 'The job listing is no longer available', 404, or expired)
  3. Experience requirement more than 3 years (> 3 yrs)
  4. Location beyond India (outside India, non-remote)
  5. Job posting date MORE THAN 2 MONTHS OLD (e.g. 'POSTED 2 MONTHS AGO', 'POSTED 3+ MONTHS AGO', or 'POSTED N YEARS AGO')
  Immediately execute 	abs(close) within 1s. Do not click Apply, do not open modals, do not snapshot, do not wait. Move immediately to the next job.
- SINGLE-JOB TAB RULE (per-agent sequential, multi-agent parallel): All agents may work in parallel, but each agent must finish the current job (fill → verify → submit → close) before opening a different tab with a different application. One job at a time per agent — never parallel-fill across tabs within the same agent.
- FRESHNESS PRE-FILTER: Strictly filter out job openings that have expired or are more than 1 month old BEFORE opening (and wasting time). Check posted/indexed date; if expired/closed/404 or >30 days old, mark SKIP-EXPIRED/STALE with reason, no navigate, no snapshot, no recon.
- ANTI-BOT DETECTION HUMAN EMULATION (MANDATORY):
  1. DEFINITELY SCROLL 4 TIMES: On every Wellfound job page, perform at least 4 smooth scrolls (25%, 50%, 75%, 100% of viewport) to trigger viewport observers, lazy components, and human behavior telemetry.
  2. SEQUENTIAL TOP-TO-BOTTOM ORDER: Complete fields/modals in natural order.
  3. RANDOM DELAYS: Add 800ms - 2200ms randomized delays between filling consecutive fields and 60ms - 180ms delay between keystrokes.
  4. 5 AGENTS MAX: Process at most 5 jobs/agents at a time.
