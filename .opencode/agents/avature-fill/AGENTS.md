# avature-fill — AGENTS.md

Platform playbook for the `avature-fill` subagent. Read this before touching any
Avature tenant (`jobs.<company>.com/Careers/...`). Shared fill loop: `initiate_fill.md`.
Master rules: `Playwright MCP Optimized Operating Prompt.md`. Raw history:
`ats/avature/observation_importance.md` (BMC, applied end-to-end 2026-09-18).

## 1. Fingerprint

- JobDetail pages (`/Careers/JobDetail/<slug>/<jobId>`) → `ApplicationMethods?jobId=...`
  (Step 1 of 2 "Select your resume") → `Register?jobId=...` (Step 2 of 2 "Personal info")
  → review/submit. Breadcrumb always shows the current step.
- First-time path needs NO login: Copy&Paste / From Device / Facebook / Google / Indeed /
  LinkedIn / Drive / Dropbox. "Already registered?" login box is optional — skip it unless
  the human is already signed in.

## 2. Resume

- "From Device" opens a NATIVE chooser: click the trigger, then `browser_file_upload`
  with the ABSOLUTE local path. Verify the filename renders inline. A stuck chooser
  clears with a paths-omitted upload call.
- Variant by JD match (`user_profile.json → resume_files`): `GenAI_DS` / `ML_Vision` /
  `ML_Vision_RL`. Verify `%PDF` magic + exact byte count first.
- The parser fills names/email/work/education/skills BUT mangles email case
  (`Jays…` → fix to exact `jays.iitkgp@gmail.com`) and leaves titles terse — verify every row.

## 3. Widget quirks (earned on BMC, don't rediscover)

- Employer / Institution / Program / visa-style combos are autocomplete comboboxes wrapping
  a textbox; State enables only after Country; Source Details options depend on Source
  (e.g. Source `Social` → `Facebook` / `LinkedIn job posting`).
- The cookie banner re-renders over Continue — dismiss via Reject before advancing.
- Continue buttons may report "not visible" while the click still submits: always re-read
  state after (URL may already be on `Register`). Continue/Next/Review/Previous are
  allowed; Submit is NEVER yours.

## 4. Source-tracing rule

- `Source` + `Source Details` are required. Prefer the link's tracking param
  (`?src=SNS-...` → `Social` + `LinkedIn job posting`) else profile default. Never leave
  parser guesses (`Job Board`/`Indeed`) unexamined, never invent a referrer.

## 5. Known-good answers (profile-backed)

- Country `India` → State `Bihar`; Address/City `Gaya`; Zip `823001`;
  Phone country-code format `+91-8651274328`; notice `Immediate`.
- Is-current-position: `No` on every ended row (profile rule — never tick current on a
  past-ended row). Relocate `Yes`; partner/sponsorship/ever-employed/relative `No`
  (India roles). Passport: optional — SKIP unless known true.
- Current position/employer mirror the latest profile role; education start `2021-08`,
  Type + Highest `Bachelor's Degree`. Skills multi-combobox: keep resume-parsed set.

## 6. Verification strings

- Success = URL `/Careers/Success?jobId=...` + heading "Thank you for applying" +
  "You have applied for <role>". An account menu with the candidate name appears.

## 7. Output contract

Per step: `RECON → PLAN → FILL → VERIFY`, no call narration. Final: filled count,
uploads, `QUEUED` items with reasons, review/success state, human next action.
Checkpoint `ats_progress.json` + `job_links.json`.
