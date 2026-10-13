# Instahyre — observation_importance.md (driver: Playwright MCP, session 2026-09-25)

## Flow shape
- Login at `/login/` (Email + Password + Login btn, Google/LinkedIn SSO). Session persists after manual login.
- Opportunities canonical URL `/candidate/opportunities/` **auto-redirects** to `/candidate/opportunities/?matching=true`.

## UI change vs roadmap (2026-09-12 map outdated)
- Old: radios Undecided / Interested / Not Interested with counts; per-card `View »` + `Not interested`; modal `Not interested` + `Apply`.
- New (observed 2026-09-25): four **buttons** acting as tabs — `Recommended jobs (N)` (= old Undecided/matching queue), `Applied jobs (N)`, `Not interested (N)`, `Search Results (N)` — followed by an `Opportunities` nav with same four links.
- Empty queue state: heading `Recommended Jobs`, text `No matching opportunities found at the moment` + `Will notify you via email when new opportunities are available.`
- Counts observed 2026-09-25: Recommended **0**, Applied **67**, Not interested **43**, Search Results 0.

## Apply-all run 2026-09-25 (+63 applies, 67→130)

- **Search Results tab is the real inventory**: header search (`Enter skills or title` + `Search`) opens
  `/candidate/opportunities/?matching=true&status=3...` with **12,992 browse-all jobs** (1,619 under
  `Data Science / Machine Learning` checkbox; `Python` skill text + DS/ML = 1,243-view used here).
  `skills=` + `job_functions=/api/v1/job_function/9` appear in URL but deep-linking a reload LOSES
  search state (`No search performed :(`) — rebuild via UI clicks every time.
- **Not-Interested list is READ-ONLY**: 43 cards render `Declined on ...` with NO `View »` button
  (verified by DOM-wide query). There is no candidate-UI path to flip NI → Apply. Record stands.
- **Search-view modal anatomy**: header quad `ROLE \n COMPANY \n LOCATION \n N-M Years` + contact +
  `Your chances of being shortlisted ... Low/Medium/High` + JD + buttons `Not interested` / `Apply`
  / `Apply on company site` (NEVER the company-site one — external flow). Some cards show a 4th
  `Front/Backend/...` tag row. Salary is NOT in the header (inside JD, not captured this run).
- **Apply mechanics**: one in-modal `Apply` click; a `similar jobs at X` popup sometimes follows with
  its own `Apply` (click it). Modal then AUTO-ADVANCES to the next listing — chain applies without
  reopening. Applied listings leave the Search set (counts drop live).
- **Modal is static**: no working × (`a.remove`/button × absent when open) and backdrop click does
  NOT close; backdrops STACK (9 observed). Only reset = reload page (reshuffles page-1 order!) +
  rebuild search. Never click modal `Not interested` on a queued/duplicate item (NI is irreversible).
- **List re-ranks constantly** (matching engine); page-1 membership shifts between loads. Target cards
  by company name via DOM (`h2` → `closest('a.row')` → parent `DIV.container` holds the
  `button.btn-interested` View), verify modal company BEFORE Apply (MISMATCH guard), capture
  location and skip hard non-India blocks (none hit; one Bangkok card seen behind modal, avoided by
  header check). All 63 applied were India/WFH.
- **Contended shared browser**: other agents retarget the current tab constantly. Same-turn
  `select`+`evaluate` pairs + `href` guards + short single-purpose calls survive; snapshots cost
  ~30k tokens and lose races — evaluate-only loops (~400 tok/call) are the way.
- **Same-company 2nds need approval** (kept QUEUED, 13 items) — see run log. Profile discrepancies
  (14 LPA vs 22-26 floor; 1y vs 18mo) still QUEUED, untouched.
## Cost / safety notes (original 2026-09-25 sweep — still valid)
- Shared live browser: other agents' tabs move the *current* tab at any time. `browser_tabs new {url}` is atomic (own tab + current in one call); `select`+act sequences race. Never fire a write (click/fill) without verifying the returned snapshot's URL/title is Instahyre.
- Read-only ops (tabs list, snapshot, evaluate) are safe anytime; navigation acts on current tab — use atomic `new` instead of select-then-navigate.
- No Apply clicks needed when Recommended = 0. Submit authority file still required before any future Apply.
- Known profile discrepancies (do NOT silently fix): Instahyre shows Current Salary Rs.14 LPA vs profile floor 22-26 LPA; 1y vs 18mo exp — both QUEUED for human.

## Apply-all run 2026-09-26 (+7 applies, 130→137)

- **Before/after**: Recommended 0 / Applied 130→137 / NI 43 unchanged / Search 1184 (Python+DS/ML) → 1555 (DS/ML-only; Python text lost on every reload — URL drops `skills=Python`, chip gone; pool widens 1184→1560).
- **Applied (7, all count-delta verified)**: UnionSys Python Dev, UnionSys GenAI/Python (modal auto-advance chain), Kahuna Sr AI/ML, IDFC Data Scientist (=appr Sr DS), Nykaa Sr Staff (=appr Sr Staff ML, DS/ML pool confirms track), OptIQ.AI MLE (tail), Neuron7 MLE (tail head). Company-match + Apply-present rationale where modal titles stuck (row title + DS/ML filter-track as backstop; Kahuna safe — both roles approved).
- **Modal detail API degraded**: 9 consecutive modals stuck at `Hold on, loading...` for h2 title (Accenture, Flipkart, Kahuna, SSTPath, Nielsen, IDFC, Nykaa, OptIQ, Neuron7). Apply button still rendered except Flipkart (only `Not interested` — possible external-flow, never force). Search/list API healthy (titles, pagination fine).
- **Blocked**: Accenture Full Stack & AI GenAI (title stuck, reloaded), Flipkart DS (no Apply btn). Skipped-unverifiable (auto-advance residues, reset via reload, never NI): SSTPath, Nielsen, Adobe.
- **Same-company guard refinements**: Tekion/Accenture company-match alone INSUFFICIENT (unapproved PM/BE/FDE/GEN-AI variants live on same pages) — title verification required when API recovers. IDFC AI Engineer, Amazon SSE, Accenture non-FullStack variants seen → QUEUED need-approval, not applied.
- **3-lane contention survival**: Naukri/Wellfound lanes retarget current tab constantly (Instahyre tab twice hijacked to Naukri profile, current-tab flips mid-wait). href/URL guards on EVERY evaluate aborted ~10 writes safely; zero wrong-tab writes. Same-turn select+evaluate rarely achievable from this client — sequential guard+verify is the workable pattern. Reload = only modal reset (reshuffles page-1, loses Python text).
- **Cost**: ~60 evaluate calls for 7 applies (~8/call incl. rebuilds after hijacks). Snapshot-to-file for checkpoint avoids 19k-token dumps.
- **Next**: 8 approved 2nds (Accenture ×2, Kahuna Backend, Tekion ML Eng, Level AI Speech, Flipkart DS?, Amazon DataEng-Salesforce, BHyve Fullstack) + tail UBDS/HyperNorm/Helfie/Quince + Backend/Fullstack/SDE views untouched.
