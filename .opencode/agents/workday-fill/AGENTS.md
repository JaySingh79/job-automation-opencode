# workday-fill — AGENTS.md

Platform playbook for the `workday-fill` subagent. Read this before touching any
`*.myworkdayjobs.com` tenant. Shared fill loop: `initiate_fill.md`. Master rules:
`Playwright MCP Optimized Operating Prompt.md`. Raw history: `ats/workday/NOTES.md`.

## 1. Fingerprint

- Job pages AND apply flows live on `<employer>.wd1|wd5.myworkdayjobs.com/<locale>/EXT/...`.
- Progress bar names steps; step count varies per tenant (Cardinal req 20184220: 6 steps —
  Autofill → My Information → My Experience → Application Questions → Voluntary
  Disclosures → Review). Never assume another tenant's count.
- "Save and Continue" advances; it is NOT the submit (Gartner correction stands).
  Terminal step is a Review page with a Submit button — stop there.

## 2. Entry

- Prefer the tenant job URL directly (`/en-US/EXT/job/<location>/<slug>_<reqId>`).
- Dead requisitions return 404 + CXS 403 on `wday/cxs/...` endpoints. That means CLOSED,
  not blocked-by-bot: search the tenant (`/en-US/EXT?q=<title>`) for a live sibling req
  (same title/team/location, new ID) and report it instead of retrying.
- Step 1 may demand Create Account / Sign In first. Pause for the human; never invent a password.

## 3. Resume

- Upload the local variant by JD match (`user_profile.json → resume_files`):
  `GenAI_DS` (GenAI/LLM/agents/general DS) / `ML_Vision` (CV/VLM/multimodal/document AI) /
  `ML_Vision_RL` (RL/decision intelligence/optimization). Verify `%PDF` magic + exact byte
  count before upload. Filename + "Successfully Uploaded!" in snapshot = proof.

## 4. Widget quirks (earned, don't rediscover)

- `data-automation-id` sits on wrapper divs — descend to `input/textarea/button`.
- Searchable prompts (Degree, Field of Study, Country codes) do NOT filter on typing.
  Open the prompt button → Search box → Enter, then pick. If the value isn't listed
  (e.g. "Metallurgical and Materials Engineering"), leave optional fields EMPTY rather
  than forcing a wrong value.
- Date sections (work From/To, education years) MUST be typed via native fill
  (`browser_fill_form`/`browser_type` on the Month/Year spinbuttons). Values set through
  `browser_evaluate` display but FAIL validation ("field required"). Phone likewise:
  pick Country Phone Code first, then type the NATIONAL number only.
- A honeypot input for robots exists — gate every generic fill on the recon `honeypot` flag.
- Stale error alerts persist after fixing fields; only the post-Continue validation counts.

## 5. Validation traps

- Errors surface ONLY as `innerText` lines starting with `Error` — not `errorMessage`,
  `role=alert`, or `aria-invalid`. Read them with one `browser_evaluate innerText` pass.
- LinkedIn URLs must contain `www.` or the field rejects.
- Role Description rejects `< > [ ] { } " \`` — sanitize (`over 90 percent`, single quotes).
- Known-good option vocab: YoE `1-3 years` (for 18mo); Degree `Bachelors`; education
  `Bachelor's / College Degree (3 or 4 years)`; English `Advanced – ...`; sponsorship `No`
  for India roles (profile-confirmed pattern). Re-verify per tenant — never assume.

## 6. Question bank defaults (profile-backed, override with explicit instruction)

- Background / criminal / drug / medical / random-drug screens: `Yes`.
- 18+: `Yes`. Authorized + docs (India): `Yes`. Non-compete: `No`. Ever employed here: `No`.
- Sponsorship (India): `No`. Relocate: `Yes`. Notice: `Immediate`.
- Source: prefer URL param (`?source=LinkedIn`) else profile default.

## 7. Output contract

Per step: `RECON → PLAN → FILL → VERIFY`, no narration of calls. Final: filled count,
uploads, `QUEUED` items with reasons, review-page state, `READY FOR HUMAN SUBMISSION`.
Checkpoint `ats_progress.json` + `job_links.json`; append new findings to `ats/workday/NOTES.md`.
