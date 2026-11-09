# Job-Application Roadmap: Instahyre + Wellfound (Playwright MCP)

Distilled from a live session (2026-09-12): 3/3 Instahyre applies, 16 Wellfound applies,
1 location-block, ~25 skips with reasons. Read this before touching either platform.
Companion files: `jobs_applied.json` (ledger), `wellfound_progress.json` (checkpoint),
`wellfound_interest_answer.md` (answer bank), `instahyre_submit_authority.json` /
`wellfound_submit_authority.json` (submit permissions).

## RULES
### 0. Standing rules (both platforms)

- NEVER invent profile facts (employment, dates, salary, skills, visa, YoE). Unknown → QUEUED, keep going.
- NEVER click final Submit/Apply without a saved `*_submit_authority.json` granted by the user in chat.
- RECON ONCE → DECIDE ONCE → ACT IN BATCHES → VERIFY ONCE. Never snapshot→fill→snapshot→fill per field.
- Verify applies by reading state back (`Applied` / `✓ Applied` in DOM, list counts), never by assuming the click worked.
- Utility/similar-jobs sidebars are the best discovery source — harvest job URLs from them, don't just page the feed.
- Even through my demand is 22 LPA+, but if you find a job that satisfies all other conditions and the salary mentioned is less than expected, `JUST FILL IT`, don't skip that; Wellfound + Instahyre
- For `instahyre`, apply to every possible `SDE/ML/AI` job, even with low chance mentioned. Maximum applications to be filled, same for `Wellfound`

### 1. Instahyre — platform map

- Login: `https://www.instahyre.com/login/` — Email + Password textboxes, Login button, Google + LinkedIn SSO.
  No Instahyre credential exists in `user_profile.json` (only Workday). Pre-filling the known email is safe;
  the password must come from the user or they log in manually in the live browser (session persists —
  after the user said "continue" we landed on `/candidate/opportunities/?matching=true` logged in).
- Opportunities: `/candidate/opportunities/` — radios Undecided / Interested / Not Interested with counts.
  Each card has `View »` (opens detail modal) + `Not interested`. Modal has `Not interested` + `Apply`.
- Apply is one click, no custom questions — profile + resume are shared automatically.
  Clicking Apply auto-advances the modal to the next job. A "similar jobs at X" popup can appear with a
  pre-checked role + its own Apply — click it to batch the sibling listing (this is how 3 applies finished in 3 clicks).
- Verify by counts: Undecided 3→0, Interested 34→37. Final state shows "No matching opportunities found".
- Profile: `/candidate/profile/` — verify 6 sections complete. Do NOT silently "fix" discrepancies:
  Instahyre showed Current Salary Rs.14 LPA vs profile min 20 LPA, and 1y vs 18mo experience — QUEUE both for the human.
- Activity: `/candidate/activity/` — Viewed (8) / Contacted / Not Shortlisted. Read-only observability.
- Warning baked into the UI: interview backouts are shown to other companies — never mass-apply blindly.

### 2. Wellfound — platform map

- Login: `https://wellfound.com/login` — Email + Password + `Log in`, plus `Continue with Google`.
  Same credential situation as Instahyre (fill known email, human supplies password or logs in manually).
- Jobs feed: `/jobs` — saved-search chips, Asia/location menu, `Filters`, `176 results` heading (drops as you apply:
  176→163 observed), location-hiding notice ("Hiding jobs that do not accept applications from your location"),
  per-card Save / Learn more / Remove / Hide / Report. `Remove` = already saved. The list is virtualized:
  only ~27–28 job links exist in the DOM at once; scrolling further barely grows it. "Saved: 7" and "Hidden" tabs exist.
- Prefer direct job URLs `https://wellfound.com/jobs/<id>-<slug>` over feed modals — they render standalone
  detail pages and avoid 10–15k-token list snapshots. Harvest IDs from cards and from "Similar jobs" sections.
- Global `/search` (Search everything box) does NOT search jobs (returns "0 results / NO RESULTS YET") — dead end.
- Apply modal variants: (a) single `What interests you about working for this company?` textbox;
  (b) `Write a note to <company>.` textbox; (c) conditional radios (location `I can relocate to…` + autocomplete,
  US-hours overlap, LLM-API Yes/No gating a follow-up textbox). Disabled textbox → resolve the dependency first:
  `snapshot(target=dialog)` ONLY in this case (never snapshot simple a/b modals) → click radio →
  `type` city `slowly:true` → click the exact suggestion → textbox enables, Send enables.
  (Validated 2026-10-11: Quadcentrix relocate-New-Delhi flow.)
- Poison tabs: a re-click in the same tab stacks zombie empty modal shells, and a modal can stick in
  `styles_loading` forever (ReactModalPortal overlay intercepts all pointer events — visible in click
  timeout logs). Fix: `tabs(close)` the poisoned tab + fresh `tabs(new)` + exactly one synthetic click;
  NEVER re-click Apply/Send inside a poisoned tab. (Validated 2026-10-11: Unize, Evam.)
- Hard block: `"<Company> is not accepting applications from your current location…"` disables ALL inputs
  + Send. Do not retry — Cancel and record BLOCKED_LOCATION (observed: Pulsora Hyderabad).
- Soft warning: `You're outside the years of experience preferred (N+ years)` still allows Send — allowed under
  submit authority (profile stays truthful; the company decides).
- JD text vs sidebar Experience often disagree (Clear Demand text said 2–5y, sidebar 5+y). Trust the stricter one
  when deciding stretch vs skip.
- Verify via BUTTON texts for `✓ Applied` (disabled), never page innerText (nav `Applied` tab
  false-positives) and never via re-snapshot.
- Watch for: external-apply instructions inside the JD ("Make sure to apply at: http://…", external Application Link)
  → DEFER, don't treat the Wellfound button as the real application (observed: Parsewave, Beyond).

### 3. Relevance filter (what earned an apply vs skip)

Apply when: role is AI/ML/DS/GenAI/agentic/RAG/eval/NLP, India or Remote-India hiring, salary touches the band
(current 14 LPA, min 20 LPA — accept range tops ≥18L for strong skill matches), exp within ~2x of 18mo
(0–2y ideal; 2–4y ok if skill-identity is exact, e.g. LangGraph+pgvector+citation-evals).
Skip taxonomy used: SENIOR_TITLE/5Y_GAP (SciSpace, AuxoAI-agent, PromptSmart, Xohani 6–9y), SALARY_FLOOR
(Boock/Gyrus/Kortexity/StrongAI/Navtech ≤10L), VOICE_OR_SECURITY_CORE_GAP (Mira 5y+ADK+night-shift, Guile
offensive-pentest, timepay TTS/ASR-expert), LEVEL_MISMATCH (intern/gig/support roles), SAME_COMPANY_2ND
(Kawa-II after Kawa-I applied, Ezeiatech-2nd), DOMAIN_OR_INFRA_MISMATCH (Bitdeer crypto-mining, Simplismart
MLOps-platform), EXTERNAL_FLOW. Special cases: ParamAIQ applied despite 5+y because the skill identity was
exact (citation graphs + lineage graphs + eval-first); AuxoAI skipped despite agent title because the JD
explicitly excluded RAG-primary backgrounds.
- Relaxed fill-max mode (user order 2026-10-11, Wellfound only): salary-floor, senior-gap soft warnings,
  same-company 2nds, 3y-non-exact and voice-AI postings are APPLIED, not skipped — Send stays enabled and
  the profile stays truthful; the company decides. SKIP only on: CLOSED_410/removed page, location hard-block
  disabling all inputs, EXTERNAL_FLOW email/apply-at instructions, login/OTP/CAPTCHA wall.

### 4. Token-cheap per-job loop (Wellfound — validated 2026-10-11, mirrors `wellfound-fill/AGENTS.md` §2+§8)

1. Fresh tab per job → direct job URL (`tabs new`; browser auto-prunes old tabs).
2. ONE `evaluate` recon: exp line, salary, ext-flow markers (`apply at|email|send resume|careers@`),
   Apply vs `✓ Applied` BUTTON texts (never page innerText — nav `Applied` tab false-positives),
   first ~400 chars of head. SKIP HERE on filter fail — no snapshot, no find (2-call skip).
3. ONE synthetic Apply click via `evaluate`
   (`Array.from(document.querySelectorAll('button')).find(x => x.innerText.trim() === 'Apply').click()`).
   NEVER trusted `click` on Apply — always times out (`element never stable` / overlay intercepts).
4. `wait_for time:3` → `find` for `What interests|Send application`. If absent → ONE reload
   (`navigate` same URL) + ONE synthetic reclick + `wait_for time:5` + `find` again. Still absent →
   record BLOCKED_MODAL_LOAD, next job. (Modal-load hangs are the only legal waits.)
5. `fill_form` the interest box (Variant A default, B ML-systems, C high-stakes, D junior) →
   ONE synthetic Send click via `evaluate`
   (`document.querySelector('[data-test="JobApplicationModal--SubmitButton"]').click()`).
   NEVER trusted `click` on Send — same timeout.
6. `evaluate` button-text check for `✓ Applied` (disabled). Report evidence in return payload only.
   No file saves of any kind, ever — no checkpoints, no ledgers, no count updates. The only
   instruction is to keep applying to jobs without stop.

### 5. Waste log — commands that should STRICTLY NOT have run

- Full-page `snapshot` after nearly every click/fill (each 10–15k tokens). Use `target=` dialog snapshots and
  `find` for verification; use `evaluate` innerText checks instead of re-snapshotting.
- `snapshot(target=<alert node>)` returning a single empty alert — check `find` output before snapshotting a target.
- Typing into the global `Search everything` box (wrong search index, 0 results) — wasted a navigate + snapshot.
- Opening full detail pages/snapshots for jobs that an `evaluate` recon would have disqualified first
  (Mira 5+y, Guile pentest+low-pay, Gyrus low-pay). Recon-before-snapshot always.
- Clicking the modal close (X) button — intercepted by the overlay and timed out; navigating resets modals for free.
- Scroll loops on the virtualized feed expecting pagination (height capped ~5052px, DOM capped ~28 links).
  Scroll+extract tops out fast; company-jobs pages (Xohani: 35 jobs, all data-eng/BI) were also dry — check
  relevance before deep-mining a company roster.
- Filling the login email before the user manually logged in anyway — harmless but redundant; one line, skip if
  the human will SSO.
- Re-asking the scope question because the first ask didn't land ("ask again") — confirm the question rendered
  before proceeding.
- `evaluate` with regex literals containing `/jobs/` inside the passed function string throws
  `SyntaxError: Invalid regular expression flags` — use `indexOf('/jobs/')` + digit match instead.
- Trusted `click` on Wellfound Apply/Send buttons (always times out: `element never stable`, overlay
  intercepts). Synthetic evaluate clicks only — zero exceptions (validated 2026-10-11).
- Re-clicking Apply/Send in a poisoned tab (zombie empty dialog / `styles_loading`-stuck modal).
  Close the tab, fresh tab, exactly one synthetic click — never re-click inside it.
- Full-page `snapshot` before the recon verdict, or `snapshot(target=dialog)` on simple (a)/(b) modals.
  Snapshot the dialog ONLY for conditional (c) modals with a disabled box.
- Over-waiting modal loads: `wait_for(3)` after Apply click is enough when healthy; only the single
  reload + `wait_for(5)` fallback may run, once. Console ad-block errors are noise — ignore them.

### 6. STRICTLY Do-not-repeat checklist

- [ ] Submit authority file exists before any Apply/Send click on that domain.
- [ ] Answer bank file exists before filling any "What interests you" box; every note traceable to profile facts.
- [ ] Salary band + exp tolerance + skip taxonomy agreed (or default to §3) before a batch, not mid-batch.
- [ ] Profile mutations (location prefs, salary, resume swap) are human-confirmed, never auto-applied mid-batch.
- [ ] No file saves of any kind — no checkpoints, no ledgers, no count updates in any file.
  The only instruction is to keep applying to jobs without stop.
