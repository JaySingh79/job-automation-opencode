---
id: search_hack
version: 2.2
purpose: Google Dork query library for finding ML/AI/GenAI jobs on ATS portals
audience: [agent, human]
last_updated: 2026-09-28
status: active
---

# Search Hack — Google Dorks for ML/AI Jobs on ATS Portals

> Copy-pasteable Google search strings for ML Engineer, AI Engineer, GenAI/LLM roles,
> and Fresher/Entry-Level openings on Greenhouse, Lever, Ashby, Workday, SmartRecruiters, Keka, Workable, Recruitee + LinkedIn posts.
> Jobs only in India or global/Asia remote roles

# Important
> Use `google_search` tool as first preference while searching using these keywords. The reponse may be slow but results are highly relevant.

## 0. How To Use This File (Agent Traversal Guide)

1. **Pick by Query ID.** Every query has a stable ID (`Q-01` … `Q-25`). Reference the ID, not the heading text.
2. **Match filters first.** Each query block lists `ATS / Role / Seniority / Geo`. Select the block whose filters match the current task before copying.
3. **Copy from `text` code fence only.** Paste verbatim into Google. Do not re-wrap lines, do not add quotes.
4. **Apply date filter.** After searching: `Tools > Any time > Past 24 hours` (fresh) or `Past week` (broad). See `§5 Execution SOP`.
5. **India/Remote tasks:** prefer `§2.2` and `§2.4`; Global tasks: prefer `§2.1` and `§2.3`.
6. **LinkedIn hiring-post tasks:** use only `§2.5`.
7. **Compose new queries** only via `§4 Composition Rules` + vocabularies in `§1`.

**Table of Contents**

- `§1` Controlled Vocabularies (ATS, Role, Seniority, Geo, Exclusions)
- `§2.1` Global Mega-Dorks (all ATS at once) — `Q-01` to `Q-03`
- `§2.2` India / Worldwide-Remote Mega-Dorks — `Q-04` to `Q-05`
- `§2.3` Platform-Specific (Greenhouse, Ashby, Lever, Workday) — `Q-06` to `Q-16`
- `§2.4` Role-Specific India/Remote (LLM, Fresher, MLOps) — `Q-17` to `Q-19`
- `§2.5` LinkedIn Posts Dorks — `Q-20`, `Q-21`, `Q-22`
- `§2.6` Simple-ATS Expansion (Keka, Workable, Recruitee) — `Q-23` to `Q-25`
- `§2.7` Freshness Patterns via `intitle:` + `after:` (JobDorking-derived) — `Q-26` to `Q-31`
- `§2.8` Aggregator-Combo + Company-Direct + `filetype:` (Yudi-derived) — `Q-32` to `Q-37`
- `§3` Negative-Filter Glossary
- `§4` Composition Rules
- `§5` Execution SOP
- `§6` Changelog

---

## 1. Controlled Vocabularies

### 1.1 ATS domains (`ATS`)

| Token | Domain | Best for |
|---|---|---|
| `greenhouse` | `site:boards.greenhouse.io` | Mid-large tech, funded startups |
| `lever` | `site:jobs.lever.co` | Startups, scale-ups |
| `ashby` | `site:ashbyhq.com` | Modern AI startups |
| `smartrecruiters` | `site:jobs.smartrecruiters.com` | Mixed mid-market |
| `keka` | `site:keka.com` | India SMB/mid-market, simple single-page form |
| `workable` | `site:apply.workable.com` | Startups/SMB, simple form + free JSON API |
| `recruitee` | `site:recruitee.com` | Startups/SMB, simple offers API |
| `workday` | `site:myworkdayjobs.com` | Enterprises, Fortune 500 |
| `linkedin-posts` | `site:linkedin.com/posts` | Founder / hiring-manager posts |
| `linkedin-jobs` | `site:linkedin.com/jobs` | LinkedIn job listings (distinct from posts) |
| `indeed` | `site:indeed.com` | Aggregator listings, India volume |
| `glassdoor` | `site:glassdoor.com` | Aggregator listings + salary context |
| `company-direct` | `site:<company>.com` | Company career-site direct (template, see Q-34) |

### 1.2 Role phrases (`ROLE`)

- Core: `"Machine Learning Engineer"`, `"ML Engineer"`, `"AI Engineer"`
- GenAI: `"LLM Engineer"`, `"Generative AI Engineer"`, `"Generative AI"`, `"GenAI"`, `"GenAI Engineer"`, `"Prompt Engineer"`, `"LLM"`, `"AI Research Engineer"`
- Adjacent: `"Data Scientist"`, `"Applied Scientist"`, `"MLOps Engineer"`, `"MLOps"`, `"AI Infrastructure"`, `"Machine Learning Platform"`, `"Machine Learning"`, `"AI"`, `"ML"`, `"Data Scientist"`

### 1.3 Seniority phrases (`SENIORITY`)

- Entry: `"Junior"`, `"Associate"`, `"Graduate"`, `"Entry Level"`, `"Fresher"`, `"Trainee"`, `"Intern"`, `"University"`, `"University Graduate"`, `"Early Career"`, `"0-1 years"`, `"0-2 years"`
- Mid/Senior: (no seniority token = all levels)

### 1.4 Geo phrases (`GEO`)

- India hubs: `"India"`, `"Bengaluru"`, `"Bangalore"`, `"Hyderabad"`, `"Pune"`, `"Gurugram"`, `"Gurgaon"`, `"Noida"`
- Remote: `"Remote"`, `"Remote - Worldwide"`, `"Remote India"`, `"Work from Anywhere"`, `"Worldwide"`, `"APAC"`

See `§3` for exclusions (`-"US Only"`, `-"UK Only"`).

### 1.5 Operator vocabulary (`OP` — new from JobDorking + Yudi, 2026-09-28)

| Operator | Syntax | Purpose | Source |
|---|---|---|---|
| `intitle:` | `intitle:"ML Engineer"` | Title must contain phrase; cuts body-match noise | JobDorking guide + board guides; Yudi `intitle:"job title"` |
| `intext:` | `intext:PyTorch` | Phrase must appear in page body (skill qualifier) | JobDorking guide |
| `after:` | `after:2026-09-01` | Pages Google considers updated after date (ISO `YYYY-MM-DD`) | JobDorking guide + all 4 board guides |
| `filetype:` | `filetype:pdf` | Restrict to file type (JD/resource PDFs, not apply pages) | Yudi |
| `AND` | `"careers" AND "ML Engineer"` | Both sides must match (company-direct pattern) | Yudi company-specific |
| Multi-`site:` OR | `(site:a OR site:b)` | Sweep several boards in one query | JobDorking ("Combine multiple boards") |

Caveats (verbatim from sources):
- `after:` is page-update date per Google, not guaranteed posting date. New listings lag 1–2 days; widen window if thin, always verify date on employer page.
- `site:` only returns indexed pages; brand-new postings may not yet be crawled.
- Bare `remote` is a keyword match, not a location filter — a page saying "no remote work" still matches.

---

## 2. Query Library

> Convention per block: `Intent` (why) → `Filters` (machine-readable) → `Query` (verbatim) → `Notes` (optional).

### 2.1 Global Mega-Dorks (All Top ATS At Once)

#### Q-01: AI & ML Engineer — All Experience Levels (Global)

- **Intent:** Broadest sweep for ML/AI/LLM roles across all major ATS.
- **Filters:** `ATS=[greenhouse, lever, ashby, smartrecruiters] | Role=[core, genai] | Seniority=any | Geo=any`
- **Query:**

```text
(site:boards.greenhouse.io OR site:jobs.lever.co OR site:ashbyhq.com OR site:jobs.smartrecruiters.com) ("Machine Learning Engineer" OR "ML Engineer" OR "AI Engineer" OR "LLM Engineer" OR "Generative AI Engineer")
```

#### Q-02: Fresher / Entry-Level / Graduate — AI & ML (Global)

- **Intent:** Entry-level AI/ML sweep across top ATS.
- **Filters:** `ATS=[greenhouse, lever, ashby] | Role=[ML, AI] | Seniority=entry | Geo=any`
- **Query:**

```text
(site:boards.greenhouse.io OR site:jobs.lever.co OR site:ashbyhq.com) ("Machine Learning" OR "AI" OR "ML") ("Junior" OR "Associate" OR "Graduate" OR "Entry Level" OR "Fresher" OR "0-1 years" OR "0-2 years")
```

#### Q-03: Location-Specific — Remote or India (Global template)

- **Intent:** Narrow Q-01 style sweep to Remote / India.
- **Filters:** `ATS=[greenhouse, lever, ashby] | Role=[ML Engineer, AI Engineer] | Seniority=any | Geo=[Remote, India]`
- **Query:**

```text
(site:boards.greenhouse.io OR site:jobs.lever.co OR site:ashbyhq.com) ("ML Engineer" OR "AI Engineer") ("Remote" OR "India")
```

### 2.2 India & Worldwide-Remote Mega-Dorks (All ATS)

> Use location inclusions + negative operators to strip region-locked jobs.

#### Q-04: AI & ML Engineer — India Office OR Remote from India / Worldwide

- **Intent:** India-based + worldwide-remote ML/AI roles at US/UK/global companies.
- **Filters:** `ATS=[greenhouse, lever, ashby, smartrecruiters] | Role=[core] | Seniority=any | Geo=[India-hubs, worldwide-remote] | Exclude=[US-Only, UK-Only]`
- **Query:**

```text
(site:boards.greenhouse.io OR site:jobs.lever.co OR site:ashbyhq.com OR site:jobs.smartrecruiters.com) ("Machine Learning Engineer" OR "ML Engineer" OR "AI Engineer" OR "LLM Engineer") ("India" OR "Bengaluru" OR "Bangalore" OR "Hyderabad" OR "Pune" OR "Gurugram" OR "Noida" OR "Remote - Worldwide" OR "Work from Anywhere") -"US Only" -"UK Only"
```

#### Q-05: Fresher / Entry-Level AI & ML — India / India Remote

- **Intent:** Entry-level AI/ML for India + India-remote.
- **Filters:** `ATS=[greenhouse, lever, ashby] | Role=[ML, AI] | Seniority=entry | Geo=[India-hubs, Remote] | Exclude=[US-Only]`
- **Query:**

```text
(site:boards.greenhouse.io OR site:jobs.lever.co OR site:ashbyhq.com) ("Machine Learning" OR "AI" OR "ML") ("Junior" OR "Associate" OR "Graduate" OR "Entry Level" OR "Fresher" OR "0-1 years" OR "0-2 years") ("India" OR "Bengaluru" OR "Bangalore" OR "Hyderabad" OR "Pune" OR "Gurugram" OR "Noida" OR "Remote") -"US Only"
```

### 2.3 Platform-Specific

#### Q-06: Greenhouse — ML / AI Engineer

- **Intent:** Mid-large tech + funded startups on Greenhouse.
- **Filters:** `ATS=[greenhouse] | Role=[ML Engineer, AI Engineer] | Seniority=any | Geo=any`
- **Query:**

```text
site:boards.greenhouse.io ("Machine Learning Engineer" OR "AI Engineer") "posted"
```

- **Notes:** `"posted"` biases to active job pages.

#### Q-07: Greenhouse — LLM / Generative AI Engineer

- **Intent:** GenAI-specific roles on Greenhouse.
- **Filters:** `ATS=[greenhouse] | Role=[genai] | Seniority=any | Geo=any`
- **Query:**

```text
site:boards.greenhouse.io ("LLM Engineer" OR "Generative AI" OR "GenAI Engineer")
```

#### Q-08: Greenhouse — Fresher / Entry-Level ML

- **Intent:** Entry-level ML/AI on Greenhouse.
- **Filters:** `ATS=[greenhouse] | Role=[ML, AI] | Seniority=entry | Geo=any`
- **Query:**

```text
site:boards.greenhouse.io ("Machine Learning" OR "AI") ("Junior" OR "Associate" OR "Graduate" OR "Entry Level")
```

#### Q-09: Greenhouse — Data Scientist / Applied Scientist / MLOps

- **Intent:** Adjacent roles on Greenhouse.
- **Filters:** `ATS=[greenhouse] | Role=[adjacent] | Seniority=any | Geo=any`
- **Query:**

```text
site:boards.greenhouse.io ("Data Scientist" OR "Applied Scientist" OR "MLOps Engineer")
```

#### Q-10: Ashby — AI Engineer & GenAI Roles

- **Intent:** Modern AI startups (Anthropic/OpenAI-ecosystem style) on Ashby.
- **Filters:** `ATS=[ashby] | Role=[genai] | Seniority=any | Geo=any`
- **Query:**

```text
site:ashbyhq.com ("AI Engineer" OR "LLM" OR "Generative AI" OR "AI Research Engineer")
```

#### Q-11: Ashby — ML Engineer (Fresher / Junior)

- **Intent:** Junior AI/ML on Ashby.
- **Filters:** `ATS=[ashby] | Role=[ML, AI] | Seniority=entry | Geo=any`
- **Query:**

```text
site:ashbyhq.com ("Machine Learning" OR "AI") ("Junior" OR "Associate" OR "University" OR "Intern")
```

#### Q-12: Ashby — MLOps / AI Infrastructure

- **Intent:** Platform/infra roles on Ashby.
- **Filters:** `ATS=[ashby] | Role=[MLOps, infra] | Seniority=any | Geo=any`
- **Query:**

```text
site:ashbyhq.com ("MLOps" OR "AI Infrastructure" OR "Machine Learning Platform")
```

#### Q-13: Lever — ML & AI Roles

- **Intent:** Startup/scale-up ML/AI roles on Lever.
- **Filters:** `ATS=[lever] | Role=[core] | Seniority=any | Geo=any`
- **Query:**

```text
site:jobs.lever.co ("Machine Learning Engineer" OR "AI Engineer" OR "ML Engineer")
```

#### Q-14: Lever — Entry-Level / Fresher AI Roles

- **Intent:** Entry-level AI/ML on Lever.
- **Filters:** `ATS=[lever] | Role=[AI, ML] | Seniority=entry | Geo=any`
- **Query:**

```text
site:jobs.lever.co ("AI" OR "Machine Learning") ("Associate" OR "Junior" OR "Graduate" OR "Entry Level")
```

#### Q-15: Workday — Enterprise AI / ML Roles

- **Intent:** Large enterprise / Fortune 500 AI/ML roles.
- **Filters:** `ATS=[workday] | Role=[ML Engineer, AI Engineer, Data Scientist] | Seniority=any | Geo=any`
- **Query:**

```text
site:myworkdayjobs.com ("Machine Learning Engineer" OR "AI Engineer" OR "Data Scientist")
```

#### Q-16: Workday — Early Career / University Graduate (Enterprise)

- **Intent:** Enterprise early-career pipeline roles.
- **Filters:** `ATS=[workday] | Role=[ML, AI] | Seniority=entry | Geo=any`
- **Query:**

```text
site:myworkdayjobs.com ("Machine Learning" OR "AI") ("Early Career" OR "University Graduate" OR "Associate")
```

### 2.4 Role-Specific — India / Global Remote (Tailored)

#### Q-17: LLM / Generative AI Engineer — US/UK Companies Hiring from India

- **Intent:** GenAI startups hiring remote in India/APAC.
- **Filters:** `ATS=[ashby, greenhouse, lever] | Role=[genai, prompt] | Seniority=any | Geo=[India, worldwide-remote, APAC] | Exclude=[US-Only]`
- **Query:**

```text
(site:ashbyhq.com OR site:boards.greenhouse.io OR site:jobs.lever.co) ("Generative AI" OR "GenAI" OR "LLM Engineer" OR "Prompt Engineer") ("India" OR "Remote - Worldwide" OR "Work from Anywhere" OR "APAC") -"US Only"
```

#### Q-18: Fresher & Early Career ML / Data Science — India Focus

- **Intent:** India fresher/graduate ML + Data Science sweep.
- **Filters:** `ATS=[greenhouse, lever, ashby] | Role=[ML, Data Scientist, AI] | Seniority=entry | Geo=[India-hubs]`
- **Query:**

```text
(site:boards.greenhouse.io OR site:jobs.lever.co OR site:ashbyhq.com) ("Machine Learning" OR "Data Scientist" OR "AI") ("Fresher" OR "Graduate" OR "Junior" OR "Trainee" OR "Associate") ("India" OR "Bangalore" OR "Bengaluru" OR "Hyderabad" OR "Gurgaon" OR "Noida" OR "Pune")
```

#### Q-19: MLOps & AI Infrastructure — India / Global Remote

- **Intent:** MLOps/platform roles for India + remote.
- **Filters:** `ATS=[greenhouse, lever, ashby] | Role=[MLOps, infra] | Seniority=any | Geo=[India-hubs, Remote] | Exclude=[US-Only]`
- **Query:**

```text
(site:boards.greenhouse.io OR site:jobs.lever.co OR site:ashbyhq.com) ("MLOps" OR "AI Infrastructure" OR "Machine Learning Platform") ("India" OR "Bengaluru" OR "Remote") -"US Only"
```

### 2.5 LinkedIn Posts Dorks (Founders & Hiring Managers)

> Finds posts where recruiters ask candidates to email/DM CVs directly.

#### Q-20: Freshers / Junior ML & AI — LinkedIn Posts (Global)

- **Intent:** Direct-apply LinkedIn posts for junior roles.
- **Filters:** `ATS=[linkedin-posts] | Role=[ML, AI] | Seniority=entry | Geo=any`
- **Query:**

```text
site:linkedin.com/posts ("hiring" OR "looking for") ("ML Engineer" OR "AI Engineer" OR "Machine Learning") ("Fresher" OR "Junior" OR "0-1 years") ("DM me" OR "email" OR "send resume")
```

#### Q-21: LLM / GenAI Engineers — LinkedIn Posts (Global)

- **Intent:** Direct-apply LinkedIn posts for GenAI roles.
- **Filters:** `ATS=[linkedin-posts] | Role=[genai] | Seniority=any | Geo=any`
- **Query:**

```text
site:linkedin.com/posts "hiring" ("LLM" OR "Generative AI" OR "AI Engineer") ("apply" OR "reach out" OR "DM")
```

#### Q-22: LinkedIn Posts — India & Global Remote Managers

- **Intent:** Indian founders/recruiters + US/UK remote-India hiring posts.
- **Filters:** `ATS=[linkedin-posts] | Role=[ML, AI] | Seniority=any | Geo=[India-hubs, Remote India, Worldwide] | Exclude=[US-Only]`
- **Query:**

```text
site:linkedin.com/posts ("hiring" OR "looking for") ("ML Engineer" OR "AI Engineer" OR "Machine Learning") ("India" OR "Bengaluru" OR "Bangalore" OR "Hyderabad" OR "Remote India" OR "Worldwide") ("DM me" OR "send CV" OR "email") -"US Only"
```

### 2.6 Simple-ATS Expansion — Keka / Workable / Recruitee (India / Remote)

> Simple-DOM only. Skip Workday-complex ATS here. Keka verified in `ats/keka/NOTES.md` (single page, no wizard). Workable + Recruitee verified via free T0 JSON APIs in `.claude/agents/ml-fresher-job-scout.md` + `runs/job_search/2026-08-12.json`.

#### Q-23: Keka — ML / AI / Data Science — India

- **Intent:** India SMB/mid-market roles on Keka (simple single-page `*.keka.com/careers/applyjob/<id>`).
- **Filters:** `ATS=[keka] | Role=[ML, AI, Data Scientist, LLM] | Seniority=any | Geo=[India-hubs, Remote] | Exclude=[US-Only]`
- **Query:**

```text
site:keka.com ("Machine Learning" OR "ML Engineer" OR "AI Engineer" OR "Data Scientist" OR "LLM") ("India" OR "Bengaluru" OR "Bangalore" OR "Hyderabad" OR "Pune" OR "Gurugram" OR "Noida" OR "Remote") -"US Only"
```

#### Q-24: Workable — ML / AI Entry + All Levels — India / Remote

- **Intent:** Startup/SMB roles on Workable (simple `apply.workable.com` form).
- **Filters:** `ATS=[workable] | Role=[ML, AI, Data Scientist, LLM] | Seniority=any | Geo=[India-hubs, Remote] | Exclude=[US-Only]`
- **Query:**

```text
site:apply.workable.com ("Machine Learning" OR "ML Engineer" OR "AI Engineer" OR "Data Scientist" OR "LLM Engineer") ("India" OR "Bengaluru" OR "Bangalore" OR "Hyderabad" OR "Pune" OR "Remote") -"US Only"
```

#### Q-25: Recruitee — ML / AI Roles — India / Remote

- **Intent:** Startup/SMB roles on Recruitee (simple offers pages + API).
- **Filters:** `ATS=[recruitee] | Role=[ML, AI, Data Scientist, LLM] | Seniority=any | Geo=[India-hubs, Remote] | Exclude=[US-Only]`
- **Query:**

```text
site:recruitee.com ("Machine Learning" OR "ML Engineer" OR "AI Engineer" OR "Data Scientist" OR "LLM") ("India" OR "Bengaluru" OR "Bangalore" OR "Hyderabad" OR "Pune" OR "Remote") -"US Only"
```

### 2.7 Freshness Patterns via `intitle:` + `after:` (JobDorking-derived)

> Source: `https://jobdorking.com/guide/` + board guides `/guide/linkedin-job-search/`, `/guide/greenhouse-job-search/`, `/guide/lever-job-search/`, `/guide/workday-job-search/` (scraped 2026-09-28).
> Pattern: `site:<board> intitle:"<Role>" <optional skill/geo keyword> after:YYYY-MM-DD`.
> Why: `intitle:` cuts body-match noise (vs bare quoted phrases in Q-01–Q-25); `after:` prioritises recently indexed pages. Set `after:` to ~45 days before run date (examples below use `2026-08-14`, matching source window). Refine one variable at a time per source guidance.

#### Q-26: Greenhouse — `intitle:` Fresh ML/AI — India / Remote

- **Intent:** Fresh Greenhouse ML/AI titles for India + remote, with less aggregator noise than Q-06.
- **Filters:** `ATS=[greenhouse] | Role=[core, genai] | Seniority=any | Geo=[India-hubs, Remote] | OP=[intitle, after] | Exclude=[US-Only]`
- **Query:**

```text
site:boards.greenhouse.io intitle:("Machine Learning Engineer" OR "ML Engineer" OR "AI Engineer" OR "LLM Engineer") ("India" OR "Bengaluru" OR "Bangalore" OR "Hyderabad" OR "Pune" OR "Remote") after:2026-08-14 -"US Only"
```

- **Notes:** Derived from JobDorking Greenhouse pattern `site:boards.greenhouse.io intitle:"UX Designer" after:2026-08-14` + skill-qualifier variant `intitle:"Software Engineer" TypeScript`. `intitle:(A OR B)` grouping works on Google; if zero results, fall back to single `intitle:"ML Engineer"`.

#### Q-27: Lever — `intitle:` Fresh ML/AI + Skill Qualifier

- **Intent:** Fresh Lever startup roles, optionally narrowed by skill token employers actually use.
- **Filters:** `ATS=[lever] | Role=[core] | Seniority=any | Geo=[India-hubs, Remote] | OP=[intitle, intext-skill, after]`
- **Query (broad):**

```text
site:jobs.lever.co intitle:("Machine Learning Engineer" OR "AI Engineer" OR "ML Engineer") ("India" OR "Bengaluru" OR "Remote") after:2026-08-14
```

- **Query (skill-narrowed, use when broad >50 results):**

```text
site:jobs.lever.co intitle:("Machine Learning Engineer" OR "AI Engineer") (Python OR PyTorch OR LLM) after:2026-08-14
```

- **Notes:** Mirrors JobDorking Lever patterns `intitle:"Data Analyst" after:...` and `intitle:"Software Engineer" senior remote after:...`. Skill term is body match (equivalent to `intext:`); add only when genuinely required.

#### Q-28: LinkedIn Jobs Section — `intitle:` Fresher ML/AI (not Posts)

- **Intent:** LinkedIn *listings* (`/jobs`) for junior ML/AI — distinct from Q-20–Q-22 which target `/posts`.
- **Filters:** `ATS=[linkedin-jobs] | Role=[ML, AI] | Seniority=entry | Geo=[India-hubs, Remote] | OP=[intitle, after]`
- **Query:**

```text
site:linkedin.com/jobs intitle:("ML Engineer" OR "AI Engineer" OR "Machine Learning Engineer" OR "Data Scientist") ("Fresher" OR "Junior" OR "Entry Level" OR "Graduate") ("India" OR "Bengaluru" OR "Bangalore" OR "Hyderabad" OR "Remote") after:2026-08-14
```

- **Notes:** Derived from JobDorking LinkedIn patterns `site:linkedin.com/jobs intitle:"Product Manager" after:...` and `intitle:"Frontend Engineer" remote after:...`. Keep to `/jobs` path to exclude profiles/posts/company pages. Try title alternatives with `OR` if too narrow.

#### Q-29: Workday — `intitle:` + City Qualifier (Enterprise India)

- **Intent:** Enterprise Workday roles in India hubs, fresh-first.
- **Filters:** `ATS=[workday] | Role=[ML Engineer, AI Engineer, Data Scientist] | Seniority=any | Geo=[India-hubs] | OP=[intitle, after]`
- **Query:**

```text
site:myworkdayjobs.com intitle:("Machine Learning Engineer" OR "AI Engineer" OR "Data Scientist") ("Bengaluru" OR "Bangalore" OR "Hyderabad" OR "Pune" OR "Gurugram" OR "Noida" OR "India") after:2026-08-14
```

- **Notes:** Derived from JobDorking Workday patterns `intitle:"Marketing Manager" after:...` and `intitle:"Financial Analyst" Chicago after:...` (city-as-qualifier). Workday titles vary by employer; if restrictive, drop `intitle:` and search key term once (per source: "Expect varied URLs and titles").

#### Q-30: Multi-Board `intitle:` Mega-Dork — Fresh ML/AI Across ATS

- **Intent:** One-query freshness sweep across Greenhouse + Lever + Ashby with title restriction.
- **Filters:** `ATS=[greenhouse, lever, ashby] | Role=[core, genai] | Seniority=any | Geo=[India-hubs, Remote] | OP=[multi-site-OR, intitle, after] | Exclude=[US-Only]`
- **Query:**

```text
(site:boards.greenhouse.io OR site:jobs.lever.co OR site:ashbyhq.com) intitle:("ML Engineer" OR "AI Engineer" OR "Machine Learning Engineer" OR "LLM Engineer") ("India" OR "Remote") after:2026-08-14 -"US Only"
```

- **Notes:** Direct application of JobDorking "Combine multiple boards with OR, wrapped in parentheses" rule to Q-04-style geo filter. Widen `after:` window if <5 results (index lag 1–2 days).

#### Q-31: `intext:` Skill Qualifier — Python / PyTorch / LLM on ATS Boards

- **Intent:** Filter ATS listings by skill appearing in JD body (GenAI-ready fresher signal).
- **Filters:** `ATS=[greenhouse, lever, ashby] | Role=[ML, AI, genai] | Seniority=entry | Geo=[India-hubs, Remote] | OP=[intext] | Exclude=[US-Only]`
- **Query:**

```text
(site:boards.greenhouse.io OR site:jobs.lever.co OR site:ashbyhq.com) ("Machine Learning" OR "AI Engineer" OR "LLM") ("Junior" OR "Fresher" OR "Entry Level" OR "Graduate") intext:(Python OR PyTorch OR LLM OR Transformers) ("India" OR "Remote") -"US Only"
```

- **Notes:** From JobDorking operator table (`intext:` = must appear in body) + Greenhouse engineering example `intitle:"Software Engineer" TypeScript`. Use one skill group at a time; `intext:(A OR B)` keeps recall.

### 2.8 Aggregator-Combo + Company-Direct + `filetype:` (Yudi-derived)

> Source: `https://yudij.substack.com/p/google-dorking-for-job-search` (scraped 2026-09-28): `site:` + `"job title"` + `"location"` combos, `intitle:"job title"`, Boolean mixing, `site:company.com "careers" AND "role"`, `filetype:pdf`.
> Why: reaches postings invisible on single-ATS sweeps (Indeed/Glassdoor mirrors, unindexed company career sites).

#### Q-32: Indeed Combo — ML/AI Title + India Location

- **Intent:** Indeed-mirrored ML/AI listings for India hubs (Yudi `site:indeed.com "software developer" "Austin"` pattern, retargeted).
- **Filters:** `ATS=[indeed] | Role=[core, adjacent] | Seniority=any | Geo=[India-hubs]`
- **Query:**

```text
site:indeed.com ("Machine Learning Engineer" OR "ML Engineer" OR "AI Engineer" OR "Data Scientist") ("Bengaluru" OR "Bangalore" OR "Hyderabad" OR "Pune" OR "Gurugram" OR "Noida" OR "India")
```

- **Query (fresher-narrowed):**

```text
site:indeed.com ("ML Engineer" OR "AI Engineer" OR "Machine Learning") ("Fresher" OR "Junior" OR "Entry Level" OR "0-1 years") ("Bengaluru" OR "Hyderabad" OR "Pune" OR "India")
```

#### Q-33: Glassdoor Combo — Boolean Mix for Fresher ML/Data Roles

- **Intent:** Glassdoor-listed internships/junior roles via Boolean `site:` + title + seniority + geo (Yudi "Combine Dorks" / data-analyst-internship-on-Glassdoor pattern).
- **Filters:** `ATS=[glassdoor] | Role=[ML, Data Scientist, AI] | Seniority=entry | Geo=[India-hubs]`
- **Query:**

```text
site:glassdoor.com ("Machine Learning" OR "Data Scientist" OR "AI Engineer") ("Intern" OR "Fresher" OR "Junior" OR "Entry Level") ("Bengaluru" OR "Bangalore" OR "Hyderabad" OR "Pune" OR "India")
```

#### Q-34: Company-Site Direct — `site:<company>.com "careers" AND "<role>"` (Template)

- **Intent:** Company career-site openings that never surface on ATS/aggregator sweeps (Yudi `site:netflix.com "careers" AND "Software Developer"` pattern).
- **Filters:** `ATS=[company-direct] | Role=[core, genai] | Seniority=any | Geo=[India, Remote]`
- **Template (replace `<company>.com` per target):**

```text
site:<company>.com ("careers" OR "career" OR "jobs") AND ("Machine Learning Engineer" OR "AI Engineer" OR "LLM Engineer")
```

- **Concrete examples (paste-ready):**

```text
site:flipkart.com ("careers" OR "jobs") AND ("Machine Learning" OR "AI Engineer" OR "Data Scientist")
```

```text
site:swiggy.com ("careers" OR "jobs") AND ("Machine Learning" OR "AI Engineer")
```

- **Notes:** Yudi source example targets Netflix/Apple; retargeted here to India-hiring product companies. One company per query (no `OR` across companies — keeps precision). Good for target-company lists.

#### Q-35: `intitle:` Internship / Trainee Finder (Yudi `intitle:"job title"` pattern)

- **Intent:** Internship-to-FTE pipeline roles (`supply-chain-intern` analogue → ML/AI intern), cross-board.
- **Filters:** `ATS=[greenhouse, lever, ashby, indeed] | Role=[ML, AI, Data Scientist] | Seniority=[Intern, Trainee] | Geo=[India-hubs, Remote]`
- **Query:**

```text
(site:boards.greenhouse.io OR site:jobs.lever.co OR site:ashbyhq.com OR site:indeed.com) intitle:("ML Intern" OR "Machine Learning Intern" OR "AI Intern" OR "Data Science Intern") ("Bengaluru" OR "Bangalore" OR "Hyderabad" OR "Pune" OR "India" OR "Remote")
```

- **Notes:** Yudi's `intitle:"supply chain intern"` + podcast-guest-Intel anecdote show `intitle:` internship titles surface hidden pipeline posts. No `after:` here for max recall; add `after:2026-08-14` only if >50 results.

#### Q-36: `filetype:pdf` — JD / Guide Finder (Resource, Not Apply Pages)

- **Intent:** Find ML/AI JD PDFs and role guides for role-language calibration (Yudi `filetype:pdf resume job role` pattern). Do NOT log as applications.
- **Filters:** `ATS=n/a (resource) | Role=[ML, AI, PM-guide-analogue] | OP=[filetype]`
- **Query:**

```text
filetype:pdf ("Machine Learning Engineer" OR "AI Engineer" OR "LLM Engineer") ("job description" OR "responsibilities" OR "qualifications") ("India" OR "Remote")
```

- **Notes:** Yudi uses `filetype:pdf` for guides/resumes; adapted to JD PDFs. Useful for extracting skill keywords to feed back into Q-27/Q-31 `intext:` qualifiers.

#### Q-37: LinkedIn Generic-Site Combo — `site:linkedin.com` Title + Hiring CTA

- **Intent:** Catch-all LinkedIn surface (jobs + posts + company updates) when `/jobs`-restricted Q-28 is too narrow (Yudi `site:linkedin.com Data Analyst job` pattern).
- **Filters:** `ATS=[linkedin-jobs, linkedin-posts] | Role=[ML, AI] | Seniority=entry | Geo=[India-hubs]`
- **Query:**

```text
site:linkedin.com ("ML Engineer" OR "AI Engineer" OR "Machine Learning") ("Fresher" OR "Junior" OR "Entry Level") ("India" OR "Bengaluru" OR "Bangalore" OR "Hyderabad") ("hiring" OR "apply" OR "DM me" OR "email")
```

- **Notes:** Broadest LinkedIn recall; deduplicate against Q-20–Q-22 and Q-28 by URL before logging.

---

## 3. Negative-Filter Glossary

| Filter | Purpose | When to append |
|---|---|---|
| `-"US Only"` | Strip US-region-locked postings | Any India / worldwide-remote query |
| `-"UK Only"` | Strip UK-region-locked postings | Worldwide-remote sweeps (Q-04) |
| `"posted"` | Bias to live Greenhouse job pages | Q-06 only |

Operator quick-ref (full defs in `§1.5`): `intitle:"..."` (title must contain), `intext:` (body must contain), `after:YYYY-MM-DD` (recently indexed pages), `filetype:pdf` (resource PDFs only, Q-36), `AND` (company-direct, Q-34).

## 4. Composition Rules (Agent Query Builder)

Template:

```text
(<ATS-CLAUSE>) (<ROLE-CLAUSE>) (<SENIORITY-CLAUSE>)? (<GEO-CLAUSE>)? (<EXCLUDE-CLAUSE>)?
```

1. `ATS-CLAUSE` = one or more `site:` tokens joined by `OR`, wrapped in parens.
2. `ROLE-CLAUSE` = one or more quoted role phrases joined by `OR`, wrapped in parens.
3. `SENIORITY-CLAUSE` = optional; omit for all-levels sweep.
4. `GEO-CLAUSE` = optional; use India-hub list + remote terms from `§1.4` for India tasks.
5. `EXCLUDE-CLAUSE` = append `-"US Only"` (and `-"UK Only"` for worldwide) when `GEO` includes India/Remote.
6. Keep each clause parenthesized. Keep `OR` uppercase. Keep phrases double-quoted.
7. Prefer 3-clause queries (ATS + Role + one of Seniority/Geo) over 4-clause for recall; add 4th clause only to narrow.
8. Freshness variant (JobDorking, Q-26–Q-30): `site:<board> intitle:(<ROLE-OR>) (<GEO>)? after:YYYY-MM-DD`. Set `after:` ≈ run-date minus 45d. Refine one variable at a time; drop `intitle:` before dropping `site:` if recall <5.
9. Aggregator/company-direct variant (Yudi, Q-32–Q-35, Q-37): `site:<aggregator|company> ("<role>") ("<city|seniority>")`. One company per query for Q-34; no `after:` on first pass for max recall.

Example — new query (Bangalore junior GenAI, Ashby+Greenhouse):

```text
(site:ashbyhq.com OR site:boards.greenhouse.io) ("LLM Engineer" OR "GenAI Engineer") ("Junior" OR "Fresher") ("Bangalore" OR "Bengaluru" OR "Remote")
```

## 5. Execution SOP

1. Paste `Query` verbatim into Google.
2. `Tools > Any time > Past 24 hours` (priority: active + early-applicant) else `Past week` (broad).
3. Open ATS links directly; skip aggregators/expired pages.
4. Deduplicate by `(company + title + ATS URL)` before logging.
5. If <5 results: drop `GEO-CLAUSE` first, then broaden `ROLE-CLAUSE` (e.g. add `"ML"` / `"AI"`).
6. If >50 results: add `SENIORITY-CLAUSE` or city token, or narrow date to 24h.
7. Log used `Q-ID + date-filter + result-count` with each run for reproducibility.

## 6. Changelog

- `2.2 (2026-09-28)` — Added `§2.7` Freshness Patterns `Q-26`–`Q-31` (`intitle:` + `after:` + `intext:` skill qualifier + multi-board OR, from `jobdorking.com/guide/` + LinkedIn/Greenhouse/Lever/Workday board guides) and `§2.8` Aggregator/Company-Direct `Q-32`–`Q-37` (Indeed/Glassdoor combos, `site:<company>.com careers AND role` template, `intitle:` intern finder, `filetype:pdf` JD finder, LinkedIn catch-all, from Yudi Substack dorking guide). Added `§1.5` operator vocab (`intitle`/`intext`/`after`/`filetype`/`AND`/multi-`site:` OR + caveats), new `§1.1` tokens (`linkedin-jobs`, `indeed`, `glassdoor`, `company-direct`), `§4` Rules 8–9, `§3` operator quick-ref. `after:` examples use `2026-08-14` source window — shift to run-date minus ~45d on use.
- `2.1 (2026-09-14)` — Added `§2.6` Simple-ATS Expansion: `Q-23` Keka, `Q-24` Workable, `Q-25` Recruitee (India/Remote, simple-DOM only, skip Workday-complex). Added `keka`/`workable`/`recruitee` to `§1.1` vocab. Fixed TOC Q-ranges to match actual sections.
- `2.0 (2026-09-12)` — Restructured for agent traversal: frontmatter, TOC, stable Q-IDs, vocabularies, code-fenced queries, composition rules, SOP. No query semantics changed; Q-13/Q-14 split Lever roles; Q-20–Q-22 grouped LinkedIn.
- `1.0` — Original flat list: global mega-dorks, platform copy-pasteables, LinkedIn dorks, India/remote variants, date-filter tip.



("ML engineer" OR "AI engineer" OR "Data Scientist") site:lever.co remote