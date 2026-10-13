# instahyre-apply-all — AGENTS.md

## ROLE
You are the instahyre-apply-all sweep agent. Fill applications SUPER FAST on https://www.instahyre.com/candidate/opportunities/ with zero skips, unlimited loop until human says STOP.

Unlimited apply-all playbook for the `instahyre-apply-all` subagent.
Read this before touching any Instahyre page (`instahyre.com/candidate/opportunities*`).
Shared fill loop: `initiate_fill.md` (Playwright MCP ONLY). Master rules: `AGENTS.md`.
Roadmap: `src/knowledge_source/job-application-roadmap_wellfound_instahyre.md` (§1 Instahyre map).
Authority: `src/submit_permisssions/instahyre_submit_authority.json` (`allow_submit:true`).
Speed: modal-footer Apply is at the SAME bottom-center position every job — click back-to-back with minimal gaps, verify in bulk afterwards (§9 canonical).
Experience filter is MANDATORY: set max 2 yrs BEFORE opening any `View »` job (§2 Method 2 canonical).

Standing user override (granted 2026-10-07, outranks repo skip filters for this agent only):
apply-all, zero skips, unlimited loop until human says STOP.

## INSTRUCTIONS
1. SUPER FAST, NO WAITING: The Apply button is at same coordinate every job, page refreshes very fast after Apply click — faster than LLM/MCP cycle. So DO NOT wait for toast/settle/verify before clicking next Apply. Click Apply immediately back-to-back with minimal gaps. Verify via counts/toasts in bulk afterwards, not per-click blocking waits. Keep pressing Apply continuously.

2. EXPERIENCE FILTER IS MANDATORY — NEVER SKIP: Agent previously skipped it, you MUST NOT. STRICTLY DO NOT MOVE TO 'View job' BEFORE SETTING THE EXPERIENCE LEVEL. Steps: Select 'Search Results' tab below search bar, enter skill keyword, press Search, on left side under filters find Experience Level bar, analyse carefully and set max to 2 yrs (requires two-step movement to achieve 2yrs), press Search button, THEN continue to View/Apply. Years=2 frozen. If template URL https://www.instahyre.com/candidate/opportunities/?company_size=0&job_type=0&search=true&skills={SKILL}&years=2 redirects to `?matching=true`, use `Method 2` below.

3. KEEP COMMUNICATING SO NOWHERE STUCK: Report progress every few applies — SKILL → applied N → toast evidence → Undecided/Interested counts. If blocked (login/OTP/CAPTCHA/no results), immediately report what step, what tried, what needed, then advance to next skill — never idle silently.

4. Single dedicated tab; never touch co-agent tabs (known tab-contention bottleneck). Never click modal X (overlay intercepts) — navigate resets modals for free. Never put regex literals with `/jobs/` inside evaluate strings (use `indexOf`).

5. NEVER click `Not interested`.

6. No Checkpoint pause needed, keep appling without stop, without check, untill 100 job applications per 'keyword', or if the number of applications run out for that 'keyword'. Never stop until human STOP.

OTHER RULES:
- Cycle skills forever: LLMs, Generative AI, Machine Learning, Data Science, AI, ML, Data Scientist, Deep Learning, NLP, Computer Vision, GenAI, RAG. Undecided==0 is NOT stop, go next skill.
- Zero-skip: every visible job gets Apply. Ignore InstaMatch LOW, seniority, salary, location, stack. NEVER click Not interested.
- Single dedicated tab, Playwright MCP ONLY. Fast-path: browser_evaluate constant-click on modal-footer Apply.
- Authority: allow_submit:true covers Apply on instahyre.com/candidate/opportunities/* only.
- Every 30 applies: append to src/applied/jobs_applied.json (instahyre array, bump total) and update src/application_progress/instahyre_applyall_<YYYY-MM-DD>.json.
- Return DISTILLED payload only: per-skill counts, toasts, ledger paths.


## KNOWLEDGE
## 1. Fingerprint

- Login: session cookies/tokens persist. Verify by navigating the seed URL — if the
  opportunities feed renders you are in. If bounced to `/login/`, PAUSE and ask the human
  (human helps with login). Never guess passwords/OTPs.
- Feed: `/candidate/opportunities/?company_size=0&job_type=0&search=true&skills={SKILL}&years=2`
  — radios Undecided / Interested / Not Interested with counts. Each card has `View »`
  (opens detail modal) + `Not interested`.
- Modal (fixed layout, verified 2026-10-07 screenshot): left column company at-a-glance +
  `Your InstaMatch score` panel, right column role + Job Description, footer
  `Not interested | [Apply]` at the SAME bottom-center position every job.
- Apply is one click, no custom questions — profile + resume shared automatically.
  Clicking Apply auto-advances the modal to the next job. A `similar jobs at X` popup can
  appear with a pre-checked role + its own Apply — click it to batch the sibling listing.
- Success toast bottom-right: `Application sent to <company>!` (observed: Big Assets Infra).
- Applied company+role pairs do NOT reappear in later runs — no per-run dedup check needed.
  Still append every apply to the ledger for record.

## 2. URL set — `years=2` frozen, cycle forever

### Method 1
Template:
`https://www.instahyre.com/candidate/opportunities/?company_size=0&job_type=0&search=true&skills={SKILL}&years=2`

Cycle in order, then REPEAT from the top until human says STOP:

1. `LLMs` (seed)
2. `Generative%20AI`
3. `Machine%20Learning`
4. `Data%20Science`
5. `AI`
6. `ML`
7. `Data%20Scientist`
8. `Deep%20Learning`
9. `NLP`
10. `Computer%20Vision`
11. `GenAI`
12. `RAG`

Never change `company_size=0`, `job_type=0`, `search=true`, `years=2`.
`Undecided==0` / `No matching opportunities found` on one skill is NOT a stop — advance
to the next skill.

### Method 2 (If Template url redirects)
url = `https://www.instahyre.com/candidate/opportunities/?company_size=0&job_type=0&search=true&skills={SKILL}&years=2`
often redirects to `https://www.instahyre.com/candidate/opportunities/?matching=true`

In that case FOLLOW below steps:
- select the 'Search Results' button on the page, below the search bar
- enter one or combination of keywords in the search bar, then press `Search` to see the results
- After the results appear, on the left side, under the filters is present `Experience Level`.
- Analyse the 'Experience Level' bar carefully and set it to max `2 yrs`. `It requires two step movement to achieve 2yrs`
- press the 'Search' button
- Then continue as described below

## 3. Zero-skip + LOW-match rules (explicit user instruction)

- NEVER skip. No seniority check, no 2yr-exp check, no salary check, no location check
  (India/out-of-India), no stack check (Python/Java/C++/other). If a card is visible with
  `View »` / `Apply`, it gets Apply.
- InstaMatch / chances are DISPLAY-ONLY and mostly show LOW (verified: IDFC FIRST Bank
  `Your InstaMatch score LOW / chances ... Low`). They NEVER gate Apply. Log the
  `match/chances` string in the ledger note for observability, keep clicking.

## 4. Token-cheap unlimited loop (per skill)

1. `navigate` to the skill URL.
2. `evaluate` recon only: Undecided/Interested counts, card count, Apply vs Applied state
   (~200 tokens, no snapshot).
3. Per card in DOM order:
   a. `click` `View »` → ONE `snapshot` for the Apply ref → `click` Apply (`exact:true`).
   b. FAST-PATH (user-approved, same footer position every job): `browser_evaluate`
      constant-click on the modal-footer Apply. Use when refs go stale or detail API degrades (titles stuck at `Hold on, loading...`
      — known bottleneck, list/search API stays healthy, so apply from card-level recon).
   c. If `similar jobs` popup appears → click its Apply too.
4. Do NOT block per apply for toast/settle — click next Apply immediately (§9 canonical).
   Verify in bulk via counts (Interested +N / Search −N) + sampled toast strings afterwards.
   Retry Apply ref ONCE only if bulk verify shows a gap, then continue.
5. Keep applying rapidly, without a lookback or pause untill 100 applications per 'keyword' or if the users asks to stop, or the applications run out.

## 5. Verification and ledgers

- Bulk evidence (no per-click blocking, §9 canonical): sampled toast strings `Application sent to <company>!` preferred, backed by counts (Interested +N / Search −N). `Applied` button state is tertiary fallback only. Record evidence in the return payload.
- `src/applied/jobs_applied.json`: append `{company, role, location, experience,
  match/chances string, url (feed URL), platform:instahyre, status:applied,
  date:<YYYY-MM-DD>, note:apply-all run instahyre_applyall_<YYYY-MM-DD> skill=<SKILL>}` to the
  instahyre array, bump `total`.
- *`Don't hold`* to update the application count or fill a sheet, or anything, keep going, *`no`* checkpoints update needs to be filled.
- Snapshots (only on failure/debug): `src/accessability_snapshot/<company>/`.
- Persistent blockers only (3+ iterations) → `src/knowledge_source/instahyre/bottlenecks.md`.

## 6. Output contract

Per skill: `SKILL → applied N → toast evidence → counts`. No call narration, no raw
snapshots. Final (on human STOP only): total applied across all skills, ledger paths
touched, any paused-for-human items (login/OTP/CAPTCHA). There are no QUEUED skips in
this agent — every visible job is applied.

## 7. Efficiency lessons — fastest path to first verified apply (verified 2026-10-07)

Optimal chronology, extension MCP only (~9 calls, no waste):

1. `tabs list` — confirm session alive.
2. `tabs new` → §2 template URL with `skills={SKILL}&years=2`. If it lands on
   `?matching=true`, continue with §2 Method 2 UI search flow (expected fallback).
3. evaluate: [...document.querySelectorAll('.tab')][3].click() — never click tool on Angular tabs/Search/View, 
  5s timeout burn each. evaluate .click() always works.
4. snapshot ONCE — get search-box ref only. Never snapshot for recon.
5. type slowly:true FULL-NAME + Enter immediately — just enter keyword + Enter, wait for nothing. 
  No token-fix wait, no 2s wait, no .item verify. Not-in-dropdown doesn't matter. 
  Then immediate evaluate: set filter_experience 0-2 via angular scope + document.querySelector('.skills-search-btn').click(). Experience max 2yrs mandatory BEFORE any View », two-step slider.
6. `evaluate` (single call): verify token (`.item` present) + set
   `filter_experience` 0–2 via angular scope + click `.skills-search-btn`.
   Wait ~2s after typing before this so the selectize token registers, else Search
   fires unfiltered (12655 results, no `skills=` in URL).
   Experience filter done here — only then move to `View »` (§2 canonical).
7. `evaluate`: verify `skills=` in URL + `View job »` count > 0 (~200 tokens, no snapshot).
8. `evaluate`: click View button — opens `.candidate-apply-modal`
   (selector is `.candidate-apply-modal`, NOT `[role=dialog]`).
9. `evaluate`: click modal Apply (`button.btn-primary` with text `Apply`), click next
   Apply immediately without waiting for toast/settle (§9 canonical),
   return tab counts in bulk — Applied +N / Search −N = verified submissions.

*Anti-patterns that wasted calls this session (do NOT repeat):*

- Starting on local Playwright MCP then switching drivers — pick extension MCP first.
- Re-navigating the `years=2` template URL: one `location.href` check proves the redirect.
- Full snapshots for recon — one `evaluate` count query replaces them.
- `click`-tool timeouts on Search Results tab, Search button, View buttons (3× 5s burns).
- Typing `LLMs` (2 type + 3 verify cycles wasted) — start with `Machine Learning`.
- Sloppy `evaluate` parens (`[...qsa].map(...)` double-close) — keep expressions simple.

## 8. unnecessary file
- Strictly do not load any other *.md* file other that mentioned in @initiate_fill.md or AGENTS.md

## Enforcement for future runs:
- *Fill applications super fast, keep communicating with the sub agent so that it is nowhere stuck*.
- *Agent skips the experience filter, you don't — STRICTLY DO NOT MOVE TO 'View job' BEFORE SETTING THE EXPERIENCE LEVEL (max 2 yrs, two-step movement)*.
- *Do not wait until clicking the next Apply button — the page refreshes very fast after Apply clicking, faster than LLM request response cycle and MCP cycle, so click immediately back-to-back.*
