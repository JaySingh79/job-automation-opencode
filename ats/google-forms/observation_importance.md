# Google Forms — fill playbook

Memory, not config. No code reads this. Goal: next Google Form is ONE clean pass, sub-minute.

## What was run (2026-08-08)

- Form: "AI Engineer - Office of the President | Pixis"
- URL: `docs.google.com/forms/d/e/<id>/viewform`
- Driver: **Playwright MCP** (`mcp__playwright__*`), local Chrome, user-directed.
- Outcome: 11 fields filled (9 required + 2 optional), human submits. G1 held.

> CLAUDE.md bans local Playwright in the sanctioned live apply path (agent-browser/Firecrawl).
> These MS/Google Forms runs were user-directed one-offs. Prefer agent-browser for real ATS runs.

## Google Forms shape

- Single scrolling page, all questions, one `Submit` + one `Clear form` button at bottom. `Page 1 of 1`.
- React-controlled. Question = `listitem` > `heading "N. <label> Required question"` + `radiogroup`/`textbox`.
- Required marker: `generic "Required question" "*"`. Top note: "* Indicates required question".
- URL fields render as `input[type=url]`, email as `input[type=email]`, phone/name/short as
  `input[type=text]`, long answers as real `textarea`. Radios are `div[role=radio][aria-checked]`.
- Section headers (e.g. "What you've built") are `heading level=2` listitems with NO input — skip them,
  don't count them as fields.
- Text inputs have NO useful `aria-label` in some dumps (`? ==`); rely on refs from the snapshot, not labels.

## FAST PATH — ~5 calls, do NOT deviate

1. `browser_navigate` -> ONE `browser_snapshot`. Gives every field ref + all radio option labels.
2. Build a checklist of EVERY required field first. **Do not skip the boring ones (email, phone).**
   Missing email+phone cost a whole extra round on the Pixis run.
3. ONE `browser_fill_form` with ALL short/url/email/text fields at once. Click each radio via `browser_click`.
4. Long free-text (the "tell us about it" prose): fill via the base64 setter below (see bug). Don't type it.
5. ONE `browser_evaluate` dump to verify, then stop. Human submits.

## THE BUG THAT WRECKS SPEED (read this)

Long English prose sent through `browser_fill_form` / `browser_type` — and even inside a
`browser_evaluate` JS string — gets **articles/filler words silently dropped** before reaching the page
("The most challenging problem I solved was building X" arrives as "most challenging problem I solved
building X"). On the Google run it also mangled JS syntax (`() => {` became `() {`). Short values
(names, URLs, emails) are unaffected — only long prose.

**Fix that always works: base64.** Encode the prose (no English words survive to be stripped), decode
in-page, set via React's native value setter. Steps:

```bash
# 1. encode (Bash tool). Heredoc keeps it out of prose-stripping.
cat <<'EOF' | base64 -w0
<full grammatical answer here>
EOF
```

```js
// 2. browser_evaluate with target=<textarea ref>, function keyword (NO arrow — arrows get mangled):
function(el){
  var text = atob("<BASE64>").trim();
  var proto = el.tagName === "TEXTAREA" ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
  Object.getOwnPropertyDescriptor(proto,"value").set.call(el, text);   // plain el.value=... won't register with React
  el.dispatchEvent(new Event("input",{bubbles:true}));
  el.dispatchEvent(new Event("change",{bubbles:true}));
  return "SET len=" + el.value.length;
}
```

Verify `len` matches the decoded length. Google Forms textareas have no matching `aria-label`, so target
the textarea by its snapshot **ref**, not by label search (that returned NOT FOUND).

## Verify-all snippet (one cheap call)

```js
function(){ var o=[]; document.querySelectorAll('input,textarea').forEach(function(e){
  if(e.value && e.type!=='hidden') o.push(e.type+' == '+e.value.slice(0,45)); });
  var r=document.querySelector('div[role=radio][aria-checked=true]');
  o.push('RADIO == '+(r?r.getAttribute('aria-label'):'none')); return o.join('\n'); }
```
Note: filter on `input[type=text]` alone MISSES url/email fields — query all `input,textarea`.

## Answer bank used (Jay Singh) — reuse verbatim

- Full name: `Jay Singh`
- Email: `jays.iitkgp@gmail.com`
- Phone: `+91-8651274328` (Google Forms text field accepts `+`/`-`; unlike MS Forms number fields which strip them)
- LinkedIn: `https://www.linkedin.com/in/jay-singh-ds/`
- GitHub: `https://github.com/JaySingh79`
- College & degree: `IIT Kharagpur - B.Tech Computer Science / Data Science, 2026`
- "Where are you right now?" radio: `0–1 years of experience` (grad Jul 2026, now Aug 2026 = fresh grad,
  NOT "Final year of college" anymore). Re-derive from graduation date vs current date each time.
- "Link to something you built with agents/LLMs" / project-link fields: `https://github.com/JaySingh79`
  (see memory `built-with-agents-link.md`).
- Portfolio / personal site: `https://jaysingh.vercel.app/`
- Any other links: `https://www.kaggle.com/jaysingh79`
- Resume link: `user_profile.json.resume_links` — `DS_Vision` (vision/CV/general) vs `DS_Vision_RL`
  (RL-heavy). Pixis (agents/automation) used `DS_Vision`. Google Drive `/view?usp=sharing` links OK.
- "Tell us about that project" prose: DFR-Tracer (Pascal AI Labs) writeup — LangGraph RAG agent, so it
  doubles as the agents/LLMs proof. Source bullets: `work_ex_details.md`.
- Current Location fields: `Gaya, Bihar` (memory `current-location-answer.md`), NOT the recent role city.

## 2026-10-04 revisit (DS Intern 6-month + PPO form)
- Revisiting a submitted form lands on "You've already responded" (title + "Your response has been
  recorded."); the "Edit your response" link reopens the filled form with all values + uploaded
  filename ("Selected files ...pdf" + Remove button) intact — fastest verify path, no re-fill needed.
- Google file-upload answers persist across sessions; here the human had uploaded
  `Resume ML_Vision_RL_PPO 7th Aug - Jay Singh.pdf` after the 2026-09-28 run (which had queued the
  GenAI_DS variant as blocked by the Drive picker). No picker retry needed when a file is present.
- Record-email checkbox state persists checked through submit/edit; radio checked states surface in
  the evaluate dump via `div[role=radio][aria-checked=true]` aria-labels (IITs / 2026).

## 2026-10-05 Scalio AI Engineer run (tab-1 Google Form)
- 12 required: 5 short (name/email/phone/resume-link/exp) + 1 radio (onsite Yes) + 6 long
  textareas (Q1 pre-filled 1109c, Q2-Q6 empty). Pre-filled values verified via dump, left intact.
- Snapshot a11y shows long answers as `textbox` but DOM truth = native `textarea`
  (`getElementsByTagName("textarea")`, order = page order: TA0=Q1..TA5=Q6). `[role=textbox]`
  selector matches nothing (implicit role, no attribute); `input,textarea` query is the
  verify path. Hidden mirrored inputs echo each answer (content-head check).
- A11y refs ROTATE after every element-targeted set (e160 worked once, e174 stale next).
  Fix: ONE page-level evaluate, index textareas by position, base64 blobs keyed inline.
- Multi-tab contention: sibling session kept stealing focus to tab 2 (SymphonyAI); tab
  selects did not stick. Guard = `location.href` check first line of every evaluate.
- Draft autosaves continuously ("Draft saved"); radios pre-checked need no click (no
  coordinate fallback needed). Submit never clicked. No file-upload widget on this form
  (resume asked as link) — Drive-picker block did not apply.

## Data sources

- `user_profile.json` — personal info, links (`portfolio`, `kaggle`, `resume_links`), screening.
- `work_ex_details.md` — authoritative work bullets (over the resume PDF).
