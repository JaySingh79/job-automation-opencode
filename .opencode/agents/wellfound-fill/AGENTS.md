# wellfound-fill — AGENTS.md

Platform playbook for the `wellfound-fill` subagent. Read this before touching any
Wellfound page (`wellfound.com/jobs*`). Shared fill loop: `initiate_fill.md`. Master rules:
`Playwright MCP Optimized Operating Prompt.md`. Roadmap: `job-application-roadmap.md`.

## 1. Fingerprint

- Login: `https://wellfound.com/login` — Email + Password + `Log in`, plus `Continue with
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

## 2. Token-cheap per-job loop

1. `navigate` to the direct job URL.
2. `evaluate` recon only: experience line, salary, Apply vs `✓ Applied` buttons (match the
   BUTTON text, not page innerText — the nav has an `Applied` tab that false-positives),
   first ~600 chars of the role description. SKIP HERE on filter fail — never snapshot.
3. `snapshot` once (Apply ref only) → `click` Apply (exact match; bare `first()` hits wrong
   buttons).
4. `find` for `What interests|Send application` → targeted `snapshot(target=dialog)` →
   `fill_form` the interest box from `wellfound_interest_answer.md` (Variant A agentic/RAG
   default, B ML-systems/eval, C healthcare/legal high-stakes, D junior build-and-learn).
5. `click` Send → `evaluate` innerText check for `✓ Applied` (disabled button). Record the
   exact evidence string.

## 3. Apply modal variants

- (a) single `What interests you about working for this company?` textbox.
- (b) `Write a note to <company>.` textbox.
- (c) conditional radios: location `I can relocate to…` + autocomplete, US-hours overlap,
  LLM-API Yes/No gating a follow-up textbox. Disabled textbox → resolve the dependency
  FIRST: click radio (via `input[value=relocate_to]` evaluate when the a11y ref is missing)
  → `type` city `slowly:true` → click the exact suggestion → textbox enables, Send enables.
- Hard block: `"<Company> is not accepting applications from your current location…"`
  disables ALL inputs + Send. Do NOT retry — Cancel, record BLOCKED_LOCATION.
- Soft warning: `You're outside the years of experience preferred (N+ years)` still allows
  Send — allowed under submit authority; profile stays truthful, the company decides.

## 4. Answers (profile-backed only)

- 18mo total experience, Immediate notice, India authorization, sponsorship `No` for India
  roles, pay `22-26 LPA (negotiable)` / numeric `22`. Prose from `work_ex_details.md` only.
- JD text vs sidebar Experience often disagree — trust the STRICTER one, note it in the
  ledger (observed: BDIPlus text 2+y vs sidebar 3+y).
- Watch for external-apply instructions inside the JD (`apply at: http://…`, external
  Application Link) → DEFER as EXTERNAL_FLOW, don't treat the Wellfound button as the real
  application (observed: Parsewave, Beyond).
- Relevance filter (roadmap §3): AI/ML/DS/GenAI/agentic/RAG/eval/NLP, India or Remote-India,
  range tops ≥18L on exact skill matches, exp within ~2x of 18mo (2–4y ok on exact identity,
  e.g. LangGraph+pgvector+citation-evals). Skip taxonomy: SENIOR_TITLE/5Y_GAP, SALARY_FLOOR
  (≤10L), VOICE_OR_SECURITY_CORE_GAP, LEVEL_MISMATCH, SAME_COMPANY_2ND,
  DOMAIN_OR_INFRA_MISMATCH, EXTERNAL_FLOW.

## 5. Verification and ledgers

- Verify via `document.body.innerText` / button-text check for `✓ Applied` (disabled), not
  via re-snapshot. Verify counts drop on the feed (`174 results` heading) as corroboration.
- `wellfound_progress.json`: applied / blocked / skipped-with-reason, `done` = len(applied);
  checkpoint every 2–3 applies. `jobs_applied.json`: append `{company, role, location,
  salary, url, status: applied}` to the wellfound array, bump `total`. `job_links.json`:
  `{Company: job_url}`. Never invent facts to satisfy a gate.
- Same-company second applications need explicit human approval (looks unfocused).

## 6. Output contract

`RECON → PLAN → FILL → VERIFY` per job, no call narration. Final: filled count, variant
used, `QUEUED` items with reasons, `✓ Applied` evidence, ledger paths touched, human next
action. Waste-log reminders: no per-field snapshots, no modal-X clicks (navigate resets
modals), no regex literals with `/jobs/` inside evaluate strings (use `indexOf`), no global
search box.

## 6. unnecessary file
- Strictly do not load any other *.md* file other that menioned in @initiate_fill.md or AGENTS.md
- Strictly do not load the *playwright-cli* based .md files when working with *playwright-mcp*
