# Plan: Test job-application automation on the IDFC posting via Steel

## Context

Goal: exercise the harness end-to-end against the `IDFC` link in `job_links.json`
(`https://careers.idfcfirst.bank.in/in/en/job/IFBAINP224648ENIN` — "Data Scientist, Mumbai"),
driving **Steel** for every browser API call, per the user's instruction.

Why this is not a plain `apply_session.py --job IDFC` run:

- **IDFC is a new ATS.** careers.idfcfirst.bank.in is a **Phenom** SPA. Exactly one ATS
  (Workday) has been driven end to end; every Phenom step/selector/terminal-step claim is
  unverified until this live run. Expect to learn the shape from scratch and record it.
- **The Steel cloud browser gets blanked.** Navigating renders the real page title
  ("Data Scientist … IDFC FIRST Bank") then the SPA collapses the tab to `about:blank`
  (`document.body.childElementCount == 0`, `content` = `<html><head></head><body></body>`).
  Classic geo/anti-bot fingerprinting of a datacenter cloud browser hitting an Indian bank
  portal. Confirmed reproducible across two navigations.
- **`apply_session.py` is Firecrawl-hardcoded** (`Session.sh()` shells out only to the
  `firecrawl` CLI; credit accounting, tmpfiles upload path, `firecrawl parse` are all
  Firecrawl-specific — `apply_session.py:33,89-141,292-308`). There is no transport seam to
  inject Steel. So this run **drives the Steel CLI directly**, reusing the same fill-then-stop
  discipline and the guard *rules*, rather than routing through that script.

User decisions (this session): **Stealth + India residential proxy**; **sign up via the live
view** with `jays.iitkgp@gmail.com` and a password I set and share back; **interactive CLI,
human clicks final Submit**.

**Output location — everything goes in a new `steel_based_automation/` folder.** This run is
decoupled from the firecrawl-era code. The rest of the repo is not needed here except: the
skills, the items already discussed this session, and `user_profile.json`; the Firecrawl scripts
are not used. So I do **not** write `ats/phenom/NOTES.md` or `kb/graph.json`. Instead every
artifact — the observation log, raw captures, and the distilled flow — lands under
`steel_based_automation/`. The observation log is written to be precise enough that a
**deterministic job-automation flow** can later be generated from it (exact selectors, waits,
option sets, field order, terminal step).

## Load-bearing invariant

**G1 / submit boundary holds on Steel exactly as on Firecrawl.** The run fills every step and
**stops on the review/terminal step without clicking Submit**. The end state is a filled
application on its review page with the human looking at it via the Steel live view — that is
success, not an incomplete run. `SUBMIT_WORDS` = `submit|finish|confirm|agree and|complete
application` (`apply_session.py:42`); no automated action may click a control matching those on
the terminal step. Only a human, in the live view, submits.

## Steel levers (CLI 0.4.4, all via `powershell -Command "steel ..."`)

- **Anti-bot:** `steel browser start --stealth` (humanize + auto-CAPTCHA) + India residential
  proxy. Confirm the exact proxy flag on `steel browser start --help` at run time
  (`-p/--proxy <url>` BYOP, and Steel-managed proxy / `-r/--region in`); use the India region.
- **Live/interactive view (human handoff):** `steel browser live --session idfc-apply` prints
  the watchable URL; also emitted as `live_url` from `steel browser start --json`. This is where
  the human does signup, any email/OTP verification, and the final Submit. `?interactive=true`
  is the default (remote mouse/keyboard on).
- **Auth persistence (survives the 15-min cap):** `--session-timeout` maxes at **900000 ms
  (15 min)** on this plan — my 1 h attempt was rejected. Signup + verification can outlast one
  session, so persist auth: start with `--profile idfc --update-profile`, and additionally export
  `steel browser cookies` + `steel browser storage` after login so a fresh session can reload
  state and resume. (`steel credentials` vault is the alternative if we store the password there.)
- **Waits:** `steel browser navigate <url> --wait-until networkidle`, then
  `steel browser wait --selector <apply-button>` / `--load-state networkidle` before snapshotting.
- **Read layers:** `snapshot -i` (accessibility tree, `@eN` refs — re-snapshot after every DOM
  change, refs go stale), `screenshot`, `content`, `get text/attr`, paren-free `eval` only
  (the wrapper passes args through bash — `()`/`{}` break; use `document.body.childElementCount`,
  not `.slice(0,800)`).
- **Evidence on failure:** `steel sessions get/logs/traces <id>`.

## Guards that still apply (rules, enforced manually while driving Steel)

- **G1** — never click a terminal-step Submit. Stop and hand off. (above)
- **G2 / upload integrity** — before the resume reaches the page, verify the local PDF at
  `user_profile.resume_file_path` (`D:\Resumes\...\Jay Resume GenAI+DS 27th July.pdf`): first 5
  bytes `%PDF-` **and** exact byte count. File is local, so verify locally (no sandbox curl
  needed), then `steel browser upload @<fileinput-ref> <path>`. Mirrors `guards.py:62`.
- **G5 / never block with a session open** — unanswered/unknown fields get queued and reported
  once at the end; do not stall mid-session. Human-only steps (signup submit, email verify, OTP,
  CAPTCHA if stealth doesn't clear it) are handed to the human via the live view, not retried in a
  loop.
- **G7 / never type into a dropdown** — enumerate the field's own options, fuzzy-match
  (floor 0.72). Below floor or unknown → queue, leave blank.

## Preconditions (0 cost)

- `preflight.py --no-probe` already run: **0 blockers, 4 warnings** (resume lags profile on 3
  roles; sponsorship=No confirmed for India). IDFC is India-based, so the G8 country caveat on
  `screening_answers.work_authorization_sponsorship` is satisfied — **sponsorship = No** holds.
- Re-verify the resume PDF exists and passes the G2 byte/magic check before Phase 4.
- Note (do not "fix"): `job_links.json` is missing the trailing comma after the HPE line, which
  breaks the `{...}`-wrap full parse. Irrelevant to a direct Steel drive (URL read directly), but
  worth flagging — the file's brace-less format is intentional; the missing comma is not.

## Execution phases

**Phase 1 — Render the page (beat about:blank).**
Start `steel browser start --session idfc-apply --stealth --profile idfc --update-profile
--session-timeout 900000` + India residential proxy. `navigate --wait-until networkidle`,
`wait --selector` for the Apply control, `snapshot -i` + `screenshot` to confirm real content.
Print `live_url` for the user. If still blank after stealth+proxy: pull `steel sessions
logs/traces`, report, and check in before thrashing (2–3 attempts max per the browser-agent rules).

**Phase 2 — Signup (human-in-the-loop via live view).**
Reach the Apply / account step. I set a **strong password**, enter email
`jays.iitkgp@gmail.com` + that password through the flow; the **human completes** anything gated
(clicking the signup submit, email verification link, OTP, CAPTCHA) in the live view. I **share
the chosen password** with the user. Immediately persist auth (`--update-profile` +
cookies/storage export) so the run survives the 15-min cap.

**Phase 3 — Survey the flow (no advancing clicks).**
`snapshot -i` each screen: enumerate steps, field labels, dropdown option sets, and the
**terminal step's real name + button text** (record, never guess). Write findings as I go into
`steel_based_automation/observations/idfc_phenom.md`, and dump the raw `snapshot`/`screenshot`/
`content` evidence into `steel_based_automation/captures/` (named per step, e.g.
`step2_snapshot.json`, `step2.png`). Every observation is timestamped and tagged with the exact
Steel command that produced it, so the log is replayable.

**Phase 4 — Fill (fill-then-stop).**
- Personal info from `user_profile.personal_information`.
- Resume: **G2 verify**, then `steel browser upload`.
- Work history from `user_profile.work_experience` (machine source of truth;
  `work_ex_details.md` is the reconciliation reference). Run free-text through the D1 illegal-char
  cleanup where a field rejects `< > [ ] { } " \`.
- Screening: from `screening_answers` (sponsorship=No, notice=Immediate, start 2026-08-10,
  source=LinkedIn). `hpe_screening_answers` are HPE-specific and **do not** carry to Phenom.
  Phenom-specific questions → **G7** enumerate/fuzzy-match; unknown/below-floor → **G5** queue,
  leave blank.
- Batch per step: snapshot → act → re-snapshot.

**Phase 5 — Stop at review (G1 handoff).**
Fill the final step but **do not** click Submit. Leave the session open on the review page.
Print: the `live_url`, the queued-questions report, and a one-line "human clicks Submit here"
instruction. The user reviews and submits themselves.

**Phase 6 — Record + distill (all in `steel_based_automation/`).**
Finalize `observations/idfc_phenom.md`: runs, flow shape, terminal step name + button text, DOM
behaviour (where validation errors surface, searchable-prompt vs dropdown vs input), the
stealth+proxy config that beat about:blank, driver = Steel + cost. Then write the first cut of a
**deterministic flow spec** at `steel_based_automation/flow/idfc.json` — an ordered list of
steps, each with its selector/ref, action, source value (or `human` for signup/verify/submit),
wait condition, and the marked `terminal_submit_step`. This is the artifact a later run replays
without an LLM in the loop. Add `steel_based_automation/README.md` naming the folder's purpose
and the working Steel invocation (stealth, India proxy, profile). Keep the Steel
profile/cookies+storage for a future resume; stop the session once the human is done (or leave it
open and tell the user the `steel browser live` command if still reviewing).

## Verification (how we know the test passed)

- Page renders real Phenom content in the live view (not `about:blank`).
- Account exists for `jays.iitkgp@gmail.com`; password shared with the user.
- Every fillable field on every step is populated from the profile; each skipped field appears in
  the end-of-run queued report with a reason.
- The run **stops on the review page with Submit unclicked**; the human can see the filled
  application in the live view and submit it.
- `steel_based_automation/` exists with: `observations/idfc_phenom.md` (flow shape + terminal
  step + about:blank fix), `captures/` (raw snapshots/screenshots per step), `flow/idfc.json`
  (deterministic replay spec), and `README.md`.

## Persist durable facts to the memory MCP

Alongside the on-disk log, write the **durable, cross-session** learnings to the official
**server-memory** MCP (`@modelcontextprotocol/server-memory`, now added to `.mcp.json` at project
scope — **pending approval** before its `mcp__memory__*` tools load). It's a knowledge graph:
model the facts as entities + observations + relations so a future session recalls them without
re-deriving:

- Entity `IDFC` (type: employer) — ATS = Phenom, portal = careers.idfcfirst.bank.in, role applied.
- Entity `Phenom` (type: ats) — observations: the Steel invocation that beat the about:blank
  block (stealth + India residential proxy + profile) as the reusable anti-bot recipe for Indian
  bank / Phenom portals; flow shape (step count, which step is terminal, its button text).
- Entity `jays.iitkgp@gmail.com` (type: account) — observation: IDFC careers account created;
  Steel auth persisted in the `idfc` profile. **Password is NOT stored in memory** (shared in chat
  only).
- Relations: `IDFC —uses→ Phenom`, `jays.iitkgp@gmail.com —registered_on→ IDFC`.

Memory holds the distilled facts; `steel_based_automation/` holds the full evidence and the
replayable spec. Observations reference the folder path. No secrets in memory.

## Confusion + newly-discovered info (user directive)

- **Never guess on ambiguity — ask.** Any point of confusion during the run (an unclear field, a
  question with no confident answer, a fork in the flow, whether an action is safe) is surfaced to
  the user via `AskUserQuestion` or the G5 queue, not resolved by assumption. This is the standing
  G5/G7 discipline made explicit.
- **Persist anything genuinely new.** If the form needs info not already in `user_profile.json`
  (a field the profile doesn't cover, an answer the user provides on the spot, a corrected value),
  write it back into `user_profile.json` — extending `unseen_fields_encountered` for form-specific
  Q&A (same schema already there: `label`, `value`, `confidence`, `reasoning`, `needs_human`), or
  the appropriate top-level section for real profile data. Then mirror the durable fact into the
  server-memory graph. `user_profile.json` holds the reusable answer; memory holds the cross-run
  learning. Nothing invented — only what the user supplies or the form confirms.

## `steel_based_automation/` layout

```
steel_based_automation/
  PLAN.md                       # this plan
  README.md                     # purpose + the working Steel invocation
  observations/idfc_phenom.md   # timestamped running log, each entry tagged with its steel cmd
  captures/                     # raw snapshot json / screenshots / content html, named per step
  flow/idfc.json                # ordered deterministic steps + terminal_submit_step (first cut)
```

## Out of scope

- No edits to `apply_session.py` / `guards.py` / core code (driving Steel directly for this test).
- No writing to `ats/phenom/NOTES.md` or `kb/graph.json` — this run is decoupled from the
  firecrawl-era code; everything lands in `steel_based_automation/`.
- No committing a reusable Steel driver (user chose interactive CLI); the `flow/idfc.json` spec is
  data, not a driver.
