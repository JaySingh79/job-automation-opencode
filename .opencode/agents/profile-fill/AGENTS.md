# profile-fill playbook — complete any user-profile page, token-cheap

## 1. Data map (read once per run, never re-read)

- `user_profile.json` — identity, contact, salary band (min pay numeric `22` = 22 LPA floor),
  `total_experience_months: 18`, education (IIT Kharagpur, B.Tech Metallurgical and
  Materials Engineering, Aug 2021–Apr 2026), 6 work roles, `resume_files` (path + bytes),
  `resume_links` (Drive URLs, URL-fields only).
- `work_ex_details.md` — prose bullets; outranks resume PDF and site-preimported data.
- `Resumes/` variants: `GenAI_DS` (GenAI/LLM/agents/general DS — default),
  `ML_Vision` (CV/VLM/multimodal/document AI), `ML_Vision_RL` (RL/optimization/planning).
- Existing page entries that are NOT in the profile (side gigs, extracurriculars) are the
  user's own data: keep them, report the discrepancy, never delete to make a save pass.

## 2. Login protocol (standing rule, from `initiate_fill.md`)

- Enter the known email yourself (`jays.iitkgp@gmail.com`); the user types passwords
  and OTPs in the live tab. The MCP browser shares the session — a login the user
  completes is visible to you on next snapshot.
- Trigger the OTP/code send yourself (e.g. Greenhouse "Send security code"), then ask
  for the code via the question tool. Never navigate away mid-login.

## 3. Token budget (hard rules — this is where runs get expensive)

- RECON: one full snapshot on landing, then ONLY `find` (single-term, e.g. `Save`,
  `Employer Name`) and `evaluate` for reading control values (inputs don't appear in
  `innerText` — query `input/textarea/select` values via JS).
- NEVER `find` with a broad regex (e.g. `option ".*"` dumps the whole page).
- NEVER full snapshot after every click/fill — reuse the snapshot each action returns.
- New repeater blocks: `snapshot(target=<container>, depth:3-4)` to get fresh refs.
- FILL in batches: one `fill_form` for all text fields per dialog; native `<select>`
  via `select_option` with exact option text; custom comboboxes via
  click → type human name → click option (or Enter ONLY on exact unique match).
- VERIFY via `evaluate` (counts/values), not re-snapshots. One closing snapshot max.
- File uploads: verify `%PDF` magic + exact byte count first
  (`uv run python -c` against `user_profile.json → resume_files` bytes); click the
  Upload/Browse trigger, then `file_upload` with the absolute path.

## 4. Save semantics (learned the hard way)

- Some pages have NO autosave (YC Work at a Startup): a reload wipes unsaved edits.
  Verify persistence by re-reading values via `evaluate`, not by assuming.
- If validation blocks Save, do NOT click it in a loop and do NOT delete user data
  to force it through: stage everything in the DOM, extract the exact error list via
  `evaluate` on `innerText` (match `please|invalid|required|missing`), and hand the
  fix list to the human. Unknown blocker values (e.g. cert years) → QUEUED question.
- Escape key can close an entire dialog AND discard its contents — prefer explicit
  Save/Cancel clicks; re-open and redo if a dialog was lost.

## 5. Platform notes

- **MyGreenhouse profile** (`my.greenhouse.io/profile`): email-OTP login (8 boxes).
  Resume upload triggers autofill — it ADDS roles but can DROP others; reconcile the
  employment list against the profile after upload. Discipline list has no
  Metallurgical → use Engineering. Salary options are USD (`< $40,000` is the only
  truthful band). Skills are free-text + Add. Self-ID: Male / not Hispanic / not a
  protected veteran / decline disability (never assert health facts).
- **YC Work at a Startup** (`/application/*`): login via `account.ycombinator.com`
  (email → Continue → password typed by user). "add another" PREPENDS new work blocks
  at the top — `first()`/`nth()` refs shift after each insert. Degree major is a
  downshift combo (type + Enter commits free text). Native month/year `<select>`s.
  Save & next validates the WHOLE page including Education certs (missing major/year
  blocks everything) — stage and hand off if blocked.
- **Weekday** (`jobs.weekday.works/profile?candidateId=…`): magic-link opens the form
  (~7% complete typical); sign-in modal can be closed to fill via the link, but saving
  needs auth — user signs in, you verify.
- **Hirist** (`hirist.tech/myprofile`): redirects home when logged out — login first.

## 6. Guards (mirror `initiate_fill.md` hard rules)

G1: last click (Submit/Apply/Send/Finish) belongs to the human, always. G2: upload
magic + byte verification. G5: queue unknowns, report once at end, never stall
mid-page. G7: never type-to-set a dropdown; enumerate options, floor for fuzzy match
or QUEUE. G11: tick only mandatory attestations. Honeypot-flagged fields are never
filled. Salary/number blocks: screenshot-slice after filling to catch runtime
validation text the DOM hides.

## 6. unnecessary file
- Strictly do not load any other *.md* file other that menioned in @initiate_fill.md or AGENTS.md
- Strictly do not load the *playwright-cli* based .md files when working with *playwright-mcp*
