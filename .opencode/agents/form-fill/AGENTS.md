# form-fill — AGENTS.md

Platform playbook for the `form-fill` subagent: Google Forms, Microsoft Forms, and
equivalent single-page form builders. Distilled from two completed live runs
(Pixis AI Engineer via Google Forms, Optum Data Scientist via MS Forms — both filled,
human submitted, G1 held). Raw histories: `ats/google-forms/observation_importance.md`,
`ats/microsoft-forms/observation_importance.md`. Shared loop: `initiate_fill.md`.

## 1. Fingerprint

- Google: `docs.google.com/forms/d/e/<id>/viewform`. Single scrolling page, `Page 1 of 1`,
  one Submit + one Clear form at the bottom. Question = `listitem` > heading
  `"N. <label> Required question"` + radiogroup/textbox. Required marker: `"*"` +
  top note `"* Indicates required question"`.
- Microsoft: `forms.cloud.microsoft/pages/responsepage.aspx?id=...`. Same single-page
  shape; headings read `"N. <label>Required to answer"`; required marker `"*"`.
- Unseen builder (Typeform/Jotform/etc.): same fast path applies — recon-first, record
  the true shape in a new `ats/<builder>/observation_importance.md`. Never force-fit.

## 2. Fast path (4–6 calls total, do not deviate)

1. `browser_navigate` → ONE `browser_snapshot` (every field ref + all radio labels at once).
2. Checklist EVERY required field FIRST — including boring ones (email, phone). Skipping
   them cost a full extra round on the Pixis run.
3. ONE `browser_fill_form` with ALL short/url/email/text fields. Click each radio via
   `browser_click` (never type into radios). Skip section headers (`heading level=2`
   listitems with NO input — not fields).
4. Long prose via the base64 React-setter path (§4), targeting the textarea by snapshot
   REF (labels are unreliable on Google Forms).
5. ONE `browser_evaluate` verify dump (§5), then stop. Human submits. Screenshots only
   for genuine visual ambiguity.

## 3. Field-type map

- Google: `input[type=url]` links, `input[type=email]`, `input[type=text]` short,
  real `textarea` long, `div[role=radio][aria-checked]` radios.
- Microsoft: everything text-like renders as `textbox` (even multi-line); single-choice
  is `radiogroup` + `radio "<label>"`. No honeypots, no illegal-char rejection observed.
- Phone: Google text fields accept `+91-8651274328` as-is; MS NUMBER fields
  (`"The value must be a number"`) strip `+`/`-` → send digits-only `8651274328`.

## 4. The prose-mangling bug (both builders — read this)

Long English prose sent through `browser_fill_form` / `browser_type` (even inside an
evaluate string) arrives with articles/filler words silently dropped. Short values are
unaffected. Fix, always: base64-encode out-of-band, decode in-page, set via React's
native value setter with input+change events, targeting the element (`function(el){...}`,
never an arrow function):

```js
function(el){
  var text = atob("<BASE64>").trim();
  var proto = el.tagName === "TEXTAREA" ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
  Object.getOwnPropertyDescriptor(proto,"value").set.call(el, text);
  el.dispatchEvent(new Event("input",{bubbles:true}));
  el.dispatchEvent(new Event("change",{bubbles:true}));
  return "SET len=" + el.value.length;
}
```

Verify returned `len` against decoded length. (Encode with `base64 -w0` over stdin so no
English crosses the stripping layer.)

## 5. Verify dump (one cheap call, builder-adjusted)

- Google: query `input,textarea` (filtering `input[type=text]` alone MISSES url/email
  fields); read the checked radio's `aria-label`.
- Microsoft: query `textarea,input[type=text],input:not([type])` mapped by placeholder.
- Mismatch on any long field → re-set via §4, re-dump, then stop.

## 6. Answer bank (Jay Singh — reuse verbatim, derive dates fresh)

- Name `Jay Singh`; email `jays.iitkgp@gmail.com`; phone per §3 by builder.
- Links: LinkedIn `https://www.linkedin.com/in/jay-singh-ds/`, GitHub
  `https://github.com/JaySingh79`, portfolio `https://jaysingh.vercel.app/`,
  Kaggle `https://www.kaggle.com/jaysingh79`.
- College: `IIT Kharagpur - B.Tech … 2026` (profile-canonical degree text).
- Experience radios: derive from graduation date vs TODAY (never reuse stale text).
- Location fields: `Gaya, Bihar` — always home, never the recent role's city.
- Resume LINK (forms want URLs, not uploads): `user_profile.json → resume_links`,
  variant by JD (`DS_Vision` vision/CV/general, `DS_Vision_RL` RL-heavy).
- Long prose: DFR-Tracer (Pascal AI Labs) writeup from `work_ex_details.md` — doubles as
  agents/LLM proof for "something you built" fields.

## 7. Output contract

Checklist (field | value | source) + radio states + dump-match confirmation + QUEUED
items + `READY FOR HUMAN SUBMISSION`. Checkpoint `ats_progress.json` + `job_links.json`.
