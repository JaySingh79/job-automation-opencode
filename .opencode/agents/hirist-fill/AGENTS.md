# hirist-fill — AGENTS.md

Playbook for the `hirist-fill` subagent. API-first: Hirist job-detail pages do NOT
hydrate in automation browsers (their Next.js chunk fails), so collect + apply through
Hirist's own JSON API via browser `evaluate`. Real page navigation ONLY for login/OTP.

## 0. Driver — Playwright MCP ONLY (strict, no exceptions)

- EVERY browser interaction goes through Playwright MCP tools. Forbidden: `playwright-cli`
  or any other CLI, external HTTP clients, OS-level automation, coordinate/vision-based
  clicking, `browser_run_code_unsafe` (`browser_evaluate` covers all JS needs).
- Allowed mapping (nothing else): `browser_navigate` (login/OTP pages only);
  `browser_evaluate` (ALL Hirist data reads + apply POSTs — same-origin fetch,
  `credentials:'include'`); `browser_snapshot` (refs for login/OTP/reachable forms only);
  `browser_fill_form` (batched login/OTP/screening fields, one call for all text fields);
  `browser_click` / `browser_type` / `browser_select_option` / `browser_file_upload`
  (login/OTP/reachable forms only — NEVER the experience combobox, job cards, or detail
  Apply buttons: stability timeouts, use `browser_evaluate`); `browser_wait_for` /
  `browser_find` (state checks, conditional reveals); `browser_tabs` (OAuth/new-tab only);
  console/network tools (debug only).
- Token discipline: ONE recon per page/step; reuse the snapshot each action returns;
  never re-snapshot without navigation, modal, conditional reveal, or stale-ref error.
  Never snapshot a job the API fields already disqualify — decide from API data first.

## 1. Fingerprint (do not re-discover)

- Board: `hirist.tech`, AI/ML category page `/c/ai-ml-jobs`. Logged-in session persists
  (verify: `fetch('https://gladiator.hirist.tech/user/profile?apply=true')` → `userId`).
  If logged out → pause and ask the human (per `initiate_fill.md`), never self-register.
- API host: `https://gladiator.hirist.tech` (same-origin fetch from any hirist.tech tab,
  `credentials:'include'`). Base category: AI/ML = `categoryId=14`.
- Detail pages (`/j/<slug>-<id>`) render SSR text but never hydrate (chunk
  `_next/static/chunks/app/j/[jobslug]/page-*.js` → ERR_PROXY_CONNECTION_FAILED, 5+
  observations). Never depend on them for applying.

## 2. Filter — the right applications (<=2 yrs)

One evaluate call, pages 0..3, `size=50`:

```js
// GET https://gladiator.hirist.tech/job/category/?minexp=0&maxexp=2&page=P&industry=&categoryId=14&size=50
// collect {id,title,min,max,loc:locations[].name,company:companyData.companyName,tags:[].name,applied}
```

- TRAP: backend filter is LOOSE — it returns overlapping ranges (min 3 / max 5 even
  with `maxexp=2`). ALWAYS enforce `job.max <= 2` client-side, then `applied == 0`.
- Keep: SDE / AI / ML / DS / GenAI / data roles, India locations (any city OK unless
  the human narrows it). Title seniority words are IGNORED — only `max <= 2` decides.
- Dedupe by numeric `id`. Never snapshot or open a job you would skip — decide from
  the API fields above.

## 3. Apply loop — exact steps (single-tab, sequential, ~800ms gap)

Per job, in this order, no deviations:

1. `evaluate` GET `job/detail?jobcode=<id>&appliedFacets=false&recommended=false&applied=false&recruiterViews=&userId=<uid>&jobType=0`
   → if `data.applied == 1`, mark applied, next job (no POST).
2. `evaluate` POST `job/apply?jobcode=<id>` body `{}` → 200 `data.id` = applicationId.
   THIS IS A FINAL SUBMIT (no review page exists). Requires submit authority.
3. 400 `ASSESSMENT_REQUIRED` → `evaluate` GET `job/assessment?jobcode=<id>` (returns
   question strings) → answer per the screening bank in §4 when a fillable form is
   reachable, else park as PENDING_ASSESSMENT with questions, next job. The
   assessment-submit endpoint is UNDISCOVERED (POST hangs, PUT and /submit /answer
   variants 404 as of 2026-10-08) — max 3 discovery probes per run, then park, never loop on it.
4. `evaluate` GET detail once → `applied == 1` is the verify evidence.
5. Checkpoint ledgers every 2–3 applies (rewrite both JSONs, counts in header).

## 4. Never (error / recurrence guards)

- NEVER POST `/job/apply` with a real jobcode for "discovery/testing" — it submits a
  real application (observed 2026-10-08: probe applied to job 1674857).
- NEVER `browser_click` the experience combobox, job cards, or detail Apply buttons —
  they time out on stability checks; use `evaluate` dispatch/click or the API instead.
- NEVER re-read `user_profile.json` / `work_ex_details.md` per job — read once per run.
- NEVER invent facts. Screening answer bank (user orders 2026-10-10, overrides profile
  defaults on Hirist): skillset/boolean questions → `Yes`; Python/ML/AI/SDE experience
  → `5` (years working with the skill incl. learning/building, NOT professional tenure —
  professional total stays 18mo; never present `5` as employment duration); all other experience questions → `2`; expected CTC → `22-26 (negotiable)` text / `22` numeric; current CTC → `18`; `Are you currently living in bangalore?` → `No`;
  `What is your current notice period?` → `10 days`; relocate → `Yes`; `Are you
  available to join immediately?` → `Yes`; WFO comfortable → `Yes`; `IIT/NIT/IIIT?`
  and `IIT background?` → `Yes`. Otherwise sponsorship `No`.
  For descriptive questions matching 'tell me what you have done', 'projects worked on', 'ML journey', 'what makes you special', or candidate overview, strictly use `src/knowledge_source/submission_pitch.md`.
- NEVER treat pause as done: on step pressure, checkpoint, park current id in output,
  resume from parked id next run. Only hard stops: login/OTP/CAPTCHA, explicit user stop.

## 5. Ledgers + output

- Queue: `src/job_search_results/hirist/hirist_<label>_<date>.json` (`{company,role,url,id,min,max,loc,status}`).
- Applied: `src/applied/hirist_<date>.json` (`{jobId,applicationId,title,company,url}` + `pending_assessment[]` with questions).
- New recurring observations → `src/knowledge_source/hirist/bottlenecks.md` (only 3+ time hindrances).
- Pending-item URLs (manual handoff): `https://www.hirist.tech/j/<slug>-<id>` where slug =
  lowercase title + first city + `<min>-<max>-yrs`, non-alphanumerics → `-` (verified exact).
- Output contract: `RECON (total/filtered counts) → APPLIED (count + evidence) → PARKED (ids + reasons) → ledgers touched → human next action`. No raw dumps.

## 6. Strict rules — 2026-10-14 (user order, no exceptions)
- SINGLE-JOB TAB RULE (per-agent sequential, multi-agent parallel): All agents may work in parallel, but each agent must finish the current job (fill → verify → submit → close) before opening a different tab with a different application. One job at a time per agent — never parallel-fill across tabs within the same agent.
- FRESHNESS PRE-FILTER: Strictly filter out job openings that have expired or are more than 1 month old BEFORE opening (and wasting time). Check posted/indexed date; if expired/closed/404 or >30 days old, mark SKIP-EXPIRED/STALE with reason, no navigate, no snapshot, no recon.
- ANTI-BOT DETECTION HUMAN EMULATION (MANDATORY):
  1. DEFINITELY SCROLL 4 TIMES: On every Hirist page, perform at least 4 smooth scrolls (25%, 50%, 75%, 100% of viewport) to trigger viewport observers, lazy components, and human behavior telemetry.
  2. SEQUENTIAL TOP-TO-BOTTOM ORDER: Complete fields in top-to-bottom visual order per modal/page.
  3. RANDOM DELAYS: Add 800ms - 2200ms randomized delays between fields and 60ms - 180ms delay between keystrokes. Never perform instantaneous bulk DOM sets.
  4. 5 AGENTS MAX: Process at most 5 jobs/agents at a time.
