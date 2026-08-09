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

## Open questions for the next Workday run

- Does the step count hold on a non-Gartner tenant?
- Has the review page's button wording changed?
- Does the local `agent-browser` driver reach the same pages with a logged-in Chrome profile, and
  what breaks that the sandbox handled?
