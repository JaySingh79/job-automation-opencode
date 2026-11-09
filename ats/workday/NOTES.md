# Workday

Only ATS driven end to end so far. One tenant, one requisition.

## Runs

### 2026-08-02 — Gartner, `gartner.wd5/EXT`, req 110911 — completed

- Driver: Firecrawl cloud (`scrape --profile` + `interact`). ~66 credits.
- Outcome: **all steps filled, automation stopped before committing.** The final review page was
  left open and the human clicked its Submit button from Firecrawl's Live View.
- "Save and Continue" on step 4 was **not** the submit. Earlier notes in this repo say otherwise —
  they are wrong. See the correction block in `CLAUDE.md`.

## Flow shape

Five steps in the progress bar. Step 4 is Voluntary Disclosures; the review page follows.
Confirm the step list per tenant before relying on it — this is one tenant's observation, not a
Workday guarantee.

## DOM behaviour

- Validation errors are **not** in `errorMessage`, `role=alert`, or `aria-invalid` text. The only
  reliable read is `innerText` lines starting with `Error` (`harvest_errors` in `guards.py`).
- `data-automation-id` sits on wrapper `div`s — descend to `input` / `textarea` / `button`.
- Searchable prompts do not filter when you type into the field. Go `promptSearchButton` → the
  Search box → Enter.
- A honeypot input labelled for robots is present. Any generic fill loop must gate on `is_honeypot`.

## Field constraints

- LinkedIn URLs must contain `www.` or the field is rejected (`validate` autofixes).
- Role Description rejects `< > [ ] { } " \` as "illegal characters". `sanitize` rewrites `>90%` to
  `over 90%` rather than dropping the claim.

### 2026-10-05 — HP, `hp.wd5/ExternalCareerSite`, req 3164655 — SKIPPED

- Driver: Playwright MCP (local), own new tab.
- Outcome: **SKIPPED, no fill.** JD live (Apply button present): `Education & Experience
  Recommended: 10+ years` + lead-scope duties (mentor senior researchers, lead large
  cross-division teams) vs 18mo profile — senior bar per fresher-scope rule.
- Tenant note: HP JD phrases YoE as "Recommended", not "Required" — softer gate than
  Cardinal/Gartner tenants, but an 8.5y gap is not a stretch. Sibling req 3164825 (same
  title/location, posted 10 days ago) almost certainly carries the same bar; recon it
  on its own merits if routed.

## Open questions for the next Workday run

- Does the step count hold on a non-Gartner tenant?
- Has the review page's button wording changed?
- Does the local `agent-browser` driver reach the same pages with a logged-in Chrome profile, and
  what breaks that the sandbox handled?

### 2026-10-29 — Deep Reconnaissance Benchmark (Mastercard, Cisco, Valeo, CorroHealth, Pitney Bowes)

- **Driver**: Local Playwright headless runner with anti-bot arguments (`--disable-blink-features=AutomationControlled`).
- **Telemetry & Ground Truth Captured**:
  1. **Legal Notice / Cookie Overlay Gate**:
     - Workday tenants (Valeo `valeo.wd3`, Pitney Bowes `pitneybowes.wd1`) inject a blocking banner overlay:
       - Wrapper: `[data-automation-id="legalNotice"]`
       - Action: Click `[data-automation-id="legalNoticeAcceptButton"]` (or `button:has-text("Accept Cookies")`) immediately upon arrival before attempting any interactions.
  2. **Dead / Stale Requisition Detection**:
     - When a Workday job is closed or expired, the server does **NOT** return HTTP 404; it returns HTTP 200 with title `Careers`.
     - Fast bailout selector: `[data-automation-id="errorMessage"]` or `[data-automation-id="errorContainer"]` displaying `"The page you are looking for doesn't exist."`. Immediately close within <= 1s.
  3. **Apply Flow & Flyout Traps**:
     - Main CTA: `[data-automation-id="adventureButton"]` (Text: "Apply").
     - On click, reveals sub-options:
       - `[data-automation-id="applyManually"]` ("Apply Manually") -> PREFERRED for deterministic field control.
       - `[data-automation-id="autofillWithResume"]` ("Autofill with Resume")
     - **CRITICAL**: Never navigate directly to `/apply/applyManually` via URL bar without session click; Workday React Router will reset to main job posting. Must click `adventureButton` then `applyManually`.
  4. **The 7-Step Enterprise Stepper**:
     - Step 1 of 7: `Create Account/Sign In`
     - Step 2 of 7: `My Information`
     - Step 3 of 7: `My Experience`
     - Step 4 of 7: `Application Questions 1 of 2`
     - Step 5 of 7: `Application Questions 2 of 2`
     - Step 6 of 7: `Voluntary Disclosures`
     - Step 7 of 7: `Review`
  5. **Step 1 Auth Controls & The "beecatcher" Honeypot**:
     - Step 1 lazily hydrates 5 input elements after a 1.5s–3.0s delay:
       - `input[data-automation-id="email"]` (Type: text)
       - `input[data-automation-id="password"]` (Type: password)
       - `input[data-automation-id="verifyPassword"]` (Type: password)
       - `input[data-automation-id="createAccountCheckbox"]` (Type: checkbox)
       - `input[data-automation-id="beecatcher"]` -> **MANDATORY HONEYPOT FILTER**. Never touch or fill `beecatcher`. Any interaction triggers silent blacklisting.
     - Mode switcher: `[data-automation-id="signInLink"]` toggles between Sign In and Create Account.
  6. **React 18 Prototype Setter Dispatch**:
     - Workday inputs are controlled by React fibers. Direct `element.value = "..."` bypasses synthetic events and fails validation.
     - Always use Playwright native `page.locator().fill(...)` or dispatch via prototype setter:
       ```javascript
       const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value')?.set;
       setter.call(el, val);
       el.dispatchEvent(new Event('input', { bubbles: true }));
       el.dispatchEvent(new Event('change', { bubbles: true }));
       el.dispatchEvent(new FocusEvent('blur', { bubbles: true }));
       ```

- Original req AIOC-S01655438-1 = CLOSED: live page renders `The page you are looking for doesn't exist` + `The page you requested was not found` (evaluate-verified). Per dead-req rule searched tenant instead of retrying.
- Tenant search `?q=Computational+Science+Associate` returns 4 live India siblings, all Associate/Analyst fresher-scope: Hyderabad Associate AIOC-S01664060-1 (21d, picked), Bengaluru BDC9A Analyst AIOC-S01665345-1 / Associate AIOC-S01665344-1 / Analyst AIOC-S01665346-1 (all 25d). JD (Hyderabad): fresh graduates, 6mo-1yr, BE/BTech, Python/OOP/DSA/SQL/REST/Git/SDLC — exact 18mo profile fit.
- Fingerprint: **7 steps** (1 Create Account/Sign In, 2 Autofill with Resume, 3 My Information, 4 My Experience, 5 Application Questions, 6 Voluntary Disclosures, 7 Review) — first 7-step Workday tenant seen (Gartner/Cardinal were 5-6). Terminal = Review with Submit; Save and Continue advances, NOT submit.
- Apply entry dialog offers 3 options: Autofill with Resume / Apply Manually / Use My Last Application. Sign-In form = Email + Password + honeypot `website` textbox for robots (flagged, never fill). Email pre-filled jays.iitkgp@gmail.com via fill_form; password never touched per standing login rule (enter email, user supplies password/OTP).
- Driver note: shared Playwright MCP browser is heavily contended (6+ agents switching current tab mid-step breaks ref validity). Extension browser (isolated, 4-5 tabs) was stable for this run — prefer it when MCP tab contention breaks refs. User deferred all Workday to last; extension tab left open at Sign In for human-last pass.
- Outcome: **0 fields past login, Submit NOT clicked.** Statuses in ats_progress.json `workday_fill_2026-10-06`: original = blocked_dead_req, Hyderabad sibling = blocked_awaiting_login_user_deferred.
