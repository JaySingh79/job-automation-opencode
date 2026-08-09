# Oracle Recruiting Cloud (Fusion HCM / CX) — fill playbook

Memory, not config. No code reads this. Goal: cut the next Oracle apply from ~15 min to ~4-5.

## What was run (2026-08-08)

- Job: "Machine Learning Scientist" — DP World, site `CX_1`, req 15097.
- Host: `*.fa.<region>.oraclecloud.com/hcmUI/CandidateExperience/...` (this one `ehpv.fa.em2`).
- Driver: **Playwright MCP** (`mcp__playwright__*`), local Chrome, user-directed.
- Outcome: 4-step flow filled end to end, human submits. G1 held.

> CLAUDE.md bans local Playwright in the sanctioned live apply path (agent-browser/Firecrawl). This was
> a user-directed test. Prefer agent-browser for real ATS runs.

## Flow shape

1. Job preview dialog -> **cookie banner** (map canvas steals the click; accept via JS, see below) ->
   `Apply Now`.
2. `/apply/email` — **email gate** ("you don't need an account"). Email + required consent checkbox +
   a **honeypot** textbox (labelled "honeypot" — DO NOT fill). Next.
3. `/apply/email` — **6-digit email verification code**. HARD human gate: can't read the inbox. Stop,
   ask user for the code, type 6 spinbuttons, Verify. (This test instance pre-filled the code; a real
   tenant will not — expect to wait.)
4. `/apply/section/1..4` — 4 steps: **1 Personal Info, 2 Job Application Questions, 3 Experience,
   4 More About You**. `Next` advances; `SUBMIT` is on step 4 only. Step nav is `1 2 3 4` at bottom.

Verifying the email **creates/loads a candidate profile**, which HEAVILY prefills every step (name,
phone, address, links, resume, cover letter, experience, education, even work-preference toggles). Most
"filling" is really **verifying prefill + fixing the few gaps/validation flags**, not typing from scratch.

## FAST PATH — target ~4-5 min (most of it the email wait)

1. Navigate to the apply URL. It bounces to the job preview.
2. Accept cookies via JS (canvas intercepts a normal click):
   `document.querySelector('.cookie-consent__button.accept').click()`
3. Click Apply Now via JS text match (avoids stale ref + canvas):
   find `button/a` whose text matches `/apply now/i`, `.click()`.
4. Email step: fill email, check consent, **skip honeypot**, Next. Ask user for the code -> fill -> Verify.
5. Each section: ONE `browser_evaluate` dumping `input,select,textarea` with label+value+required
   (snippet below) to see prefill + gaps in one call. Then only touch gaps.
6. **BEFORE filling any pay/salary block, screenshot it first** (see the big gotcha). Same for any
   section with money or conditional fields.
7. Advance with `page.locator("button:has-text('Next')").click()`. Stop on step 4. Human submits.

## THE GOTCHAS THAT COST THE 15 MIN

- **DOM attributes lie about validation.** `input[name=minimumPay]` reported `type=text`, no `pattern`,
  no `inputmode` — but at runtime it (a) enforced **numeric only** ("Enter a whole number." error) and
  (b) had a hidden **`maxlength=18`** that silently truncated `base>=18+4(negotiable)` to `...negotia`.
  The truncation and the numeric rule were ONLY visible in a screenshot, not in `evaluate` of attrs.
  **Lesson: screenshot money/validated fields before trusting them; check `e.value.length` vs input
  after filling.** User's standing rule for pay fields: free-text field -> `base>=18+4(negotiable)`;
  numeric-only field -> `20` (i.e. 20 LPA). This field was numeric -> `20`.
- **Conditional required fields appear only after you fill a trigger.** Entering Minimum Pay revealed
  **Currency Code *** and **Pay Frequency *** (both required) that weren't there before. Screenshot after
  filling a money field to catch the new required siblings.
- **Oracle comboboxes: open -> type the NAME (not the code) -> pick the gridcell.** They render options
  as `grid`/`gridcell` in a portal (invisible to `[role=option]` queries). `INR` returned "No results";
  `Indian Rupee` returned 1 match. Language: type `English`, pick the plain `English` gridcell (not
  `English (Australia)` etc.). Country/State are `combobox` too.
- **File-chooser modal freezes everything.** A stray click on a `Resume` / upload button opens a native
  file chooser; while open, `browser_evaluate`/`browser_press_key` all error with "does not handle the
  modal state". Clear it with `browser_file_upload` (no `paths` = cancel) — may need to call it once
  per open chooser. **Never click near Resume/upload/import buttons.**
- **`role=radiogroup`/`fieldset` generic scrapes miss the questions.** Yes/No answers render as
  `list > listitem > button "Yes"/"No"`, selected = `[pressed]`. Screening question text is best read
  via `document.querySelector('main').innerText`, not the a11y tree.
- Prefilled Yes/No use color, not the a11y `pressed` reliably in screenshots (orange = selected).
- Some prefilled data is WRONG (imported from resume-parse / old profile): saw phantom "Materials
  Science" education, an "Affine" role, and dates off by a year vs `user_profile.json`. Flag these to
  the user; don't silently trust step 3.

## Handy snippets

Dump all fields + required flags (one call per section):
```js
function(){ var o=[]; document.querySelectorAll('input,select,textarea').forEach(function(e){
  if(e.type==='hidden') return; var l=e.getAttribute('aria-label')||e.name||e.id||'?';
  var r=e.getAttribute('aria-required')==='true'||e.required;
  o.push((r?'*':' ')+' ['+e.tagName.toLowerCase()+':'+e.type+'] '+l.slice(0,40)+' = ['+(e.value||'').slice(0,40)+']'); });
  return o.join('\n'); }
```
Read a section's questions/prose:
```js
function(){ return document.querySelector('main').innerText.replace(/\n{2,}/g,'\n').slice(0,2500); }
```
Verify errors / "all set":
```js
function(){ var o=[]; document.querySelectorAll('main [role=alert],main [class*=error]').forEach(function(x){
  var t=(x.textContent||'').replace(/\s+/g,' ').trim(); if(t&&t.length<60) o.push(t); }); return o.join(' | '); }
```
(NB: Oracle shows "You're all set, Jay!" as a `[role=alert]` — that's success, not an error.)

## Answers used this run (Jay Singh)

- Contact: prefilled from profile (phone `+91 8651274328`, India, Gaya address, gender Male).
- Step 2 screening: "Have you ever worked for a DP World company in the past?" -> **No**.
- Languages: **English** (the imported "Unnamed Language" row had a required blank Language field ->
  "Fields to fix: 1"; Edit -> set Language = English -> Save. Proficiency/Native are optional).
- Work Preferences: from `user_profile.json.work_preferences` — Travel Domestically Yes, Travel
  Internationally No, Willing to Relocate Yes, All Locations Yes, Length "2", Reason "Work from office
  preferred, hybrid would be great", Comments "By 2 it means 2 years".
- Minimum Pay `20`, Currency `Indian Rupee`, Pay Frequency `Yearly` (LPA = per annum).
- E-Signature: Full Name (required) = `Jay Singh`.
- Resume + Cover Letter were already attached by the profile; Links 1/2/3 = portfolio/kaggle/github.

## Data sources

- `user_profile.json` — personal info, `work_preferences` (incl. `minimum_pay_text`/`minimum_pay_numeric`),
  `resume_links`, links.
- `work_ex_details.md` — authoritative work bullets (over resume PDF and over Oracle's imported step-3 data).
