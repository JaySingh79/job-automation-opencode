# Microsoft Forms — fill playbook

Memory, not config. No code reads this. Goal: next MS Forms fill is fast + cheap on tokens.

## What was run (2026-08-08)

- Form: "Data Scientist Hiring @ Optum (Pune) | AI x Healthcare"
- URL host: `forms.cloud.microsoft/pages/responsepage.aspx?id=...&route=shorturl`
- Driver: **Playwright MCP** (`mcp__playwright__*`), local Chrome. User picked it explicitly.
- Outcome: 8 fields filled, human clicked Submit. G1 held (automation never submitted).

> Note: CLAUDE.md bans local Playwright in the **live apply path** (agent-browser/Firecrawl only).
> This was a user-directed one-off test, not the sanctioned path. Prefer agent-browser for real runs.

## MS Forms shape (what to expect)

- Single scrolling page, all questions at once, one `Submit` button at the bottom. No multi-step wizard.
- Fields are React-controlled. Question N heading = `heading "N. <label>Required to answer"`.
- Text fields render as `textbox` (even multi-line "descriptive" answers report as `input`, not `textarea`).
- Single-choice = `radiogroup` with `radio "<option label>"`. Click the radio ref; don't type.
- Required marker: `note "Required to answer" "*"`.
- No honeypots, no illegal-char rejection (that was Workday), no searchable prompts observed.

## Fast path (minimum tokens, minimum round-trips)

1. `browser_navigate` then ONE `browser_snapshot` — gives every field ref + radio options in one shot.
   Do not re-snapshot per field; the first snapshot has it all.
2. Batch all text fields in a single `browser_fill_form` call. Click each radio with `browser_click`.
3. `browser_evaluate` once to dump all input values for verification (see snippet below).
4. Leave open; human submits.

That is 4-5 tool calls total. Skip screenshots unless asked.

## GOTCHAS that cost tokens/correctness

- **`browser_fill_form` / `browser_type` stripped articles from the long descriptive answer** — the DOM
  value came out grammatically broken ("The most challenging problem I solved was building" became
  "most challenging problem I solved building"). Short fields (name, email, URL) were fine; only the
  long prose field mangled. **Always verify long free-text fields** after fill, and if broken, set the
  value via JS native setter (React-safe):

  ```js
  () => {
    const el = Array.from(document.querySelectorAll('textarea,input')).find(e => e.value.includes('<unique-token>'));
    const proto = el.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
    Object.getOwnPropertyDescriptor(proto,'value').set.call(el, FULL_TEXT);
    el.dispatchEvent(new Event('input',{bubbles:true}));
    el.dispatchEvent(new Event('change',{bubbles:true}));
  }
  ```
  Plain `el.value = ...` does NOT register with React — must use the prototype setter + input event.

- **Number fields** (placeholder "The value must be a number") reject `+`/`-`. Phone `+91-8651274328`
  went in as `8651274328`. Strip non-digits for any numeric field.

- Verify-all-values snippet (one call, cheap):
  ```js
  () => Array.from(document.querySelectorAll('textarea,input[type=text],input:not([type])'))
    .map(e => (e.placeholder||'?').slice(0,25)+' == '+e.value).join('\n')
  ```

## Answer bank used (Jay Singh) — reuse verbatim

- Name: `Jay Singh`
- Email: `jays.iitkgp@gmail.com`
- Contact (digits only): `8651274328`
- Years professional experience: `< 4 years` (fresh B.Tech Jul 2026, all roles internships)
- Current/Last Company: `Pibit AI (YC W21)` (most recent by date)
- **Current Location: `Gaya, Bihar`** — always this, NOT the recent role's city. See memory
  `current-location-answer.md` and `user_profile.json.personal_information.current_location`.
- Resume link: from `user_profile.json.resume_links`. Two variants —
  `DS_Vision` (vision/CV/VLM roles) vs `DS_Vision_RL` (RL-heavy roles). Optum was vision → used `DS_Vision`.
  These are Google Drive `/view?usp=sharing` links; publicly viewable in incognito, accepted by the URL field.
- Descriptive "most challenging problem" answer: the DFR-Tracer (Pascal AI Labs) writeup. Source of
  truth for work bullets is `work_ex_details.md`, not the resume PDF.

## Data sources

- Personal/screening/work: `user_profile.json`.
- Work bullets prose: `work_ex_details.md` (authoritative over resume PDF).
