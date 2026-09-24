# Job-Application Roadmap: Instahyre + Wellfound (Playwright MCP)

Distilled from a live session (2026-09-12): 3/3 Instahyre applies, 16 Wellfound applies,
1 location-block, ~25 skips with reasons. Read this before touching either platform.
Companion files: `jobs_applied.json` (ledger), `wellfound_progress.json` (checkpoint),
`wellfound_interest_answer.md` (answer bank), `instahyre_submit_authority.json` /
`wellfound_submit_authority.json` (submit permissions).

## 0. Standing rules (both platforms)

- NEVER invent profile facts (employment, dates, salary, skills, visa, YoE). Unknown → QUEUED, keep going.
- NEVER click final Submit/Apply without a saved `*_submit_authority.json` granted by the user in chat.
- RECON ONCE → DECIDE ONCE → ACT IN BATCHES → VERIFY ONCE. Never snapshot→fill→snapshot→fill per field.
- Verify applies by reading state back (`Applied` / `✓ Applied` in DOM, list counts), never by assuming the click worked.
- Checkpoint progress to `wellfound_progress.json` every 2–3 applies (applied / blocked / skipped-with-reason).
- Utility/similar-jobs sidebars are the best discovery source — harvest job URLs from them, don't just page the feed.

## 1. Instahyre — platform map

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

## 2. Wellfound — platform map

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
  US-hours overlap, LLM-API Yes/No gating a follow-up textbox). Disabled textbox → resolve the dependency first
  (click radio → type city → click exact suggestion → textbox enables, Send enables).
- Hard block: `"<Company> is not accepting applications from your current location…"` disables ALL inputs
  + Send. Do not retry — Cancel and record BLOCKED_LOCATION (observed: Pulsora Hyderabad).
- Soft warning: `You're outside the years of experience preferred (N+ years)` still allows Send — allowed under
  submit authority (profile stays truthful; the company decides).
- JD text vs sidebar Experience often disagree (Clear Demand text said 2–5y, sidebar 5+y). Trust the stricter one
  when deciding stretch vs skip, note it in the ledger.
- Verify via `document.body.innerText` containing `Applied` / `✓ Applied` (disabled button), not via snapshot.
- Watch for: external-apply instructions inside the JD ("Make sure to apply at: http://…", external Application Link)
  → DEFER, don't treat the Wellfound button as the real application (observed: Parsewave, Beyond).

## 3. Relevance filter (what earned an apply vs skip)

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

## 4. Token-cheap per-job loop (Wellfound)

1. `navigate` to direct job URL.
2. `evaluate` recon only: experience line, salary, Apply/Applied buttons, first ~600 chars of About (≈200 tokens,
   no snapshot). SKIP HERE if it fails the §3 filter — never snapshot a job you won't apply to.
3. `snapshot` once (only to get the Apply ref) → `click` Apply (use `exact: true`; bare `first()` hits wrong buttons).
4. `find` for `What interests|Send application` → targeted `snapshot(target=dialog)` → `fill_form` from
   `wellfound_interest_answer.md` Variant A/B/C/D (company + role names specific, 1–2 real numbers max).
5. `click` Send → `evaluate` innerText check for `Applied`. Update checkpoint file.

## 5. Waste log — commands that should NOT have run

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

## 6. Do-not-repeat checklist

- [ ] Submit authority file exists before any Apply/Send click on that domain.
- [ ] Answer bank file exists before filling any "What interests you" box; every note traceable to profile facts.
- [ ] Salary band + exp tolerance + skip taxonomy agreed (or default to §3) before a batch, not mid-batch.
- [ ] Same-company second applications need explicit approval (looks unfocused).
- [ ] Profile mutations (location prefs, salary, resume swap) are human-confirmed, never auto-applied mid-batch.
- [ ] Progress JSON updated every 2–3 applies; final `jobs_applied.json` written at the end.
