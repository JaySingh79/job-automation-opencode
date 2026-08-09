# ats/ — per-ATS knowledge folders

One folder per **ATS product**, not per employer. Tenants of the same product share a flow, so
`gartner.wd5` and any other Workday tenant both land in `workday/`.

```
ats/<product>/
  NOTES.md     # prose memory. Hand-written. No code reads it.
  *.json       # raw captures, or observations waiting to be harvested into the graph.
```

## What goes in NOTES.md

What a human or agent would otherwise have to rediscover on the next application:

- How many steps, and what each one is called.
- **Which step is terminal, and what its button says.** Never guess this; record what was seen.
- Which fields are plain inputs vs. searchable prompts vs. dropdowns.
- Where validation errors actually appear in the DOM.
- Which driver was used (Firecrawl cloud / agent-browser local), and what it cost.
- Anything that failed, and what the failure looked like.

Write it during or immediately after the run, while the session is fresh.

## What does NOT go here

`kb/graph.json` is the only source of truth for anything code reads — selectors, answers,
constraints, `terminal_submit_step`. When a note becomes actionable, fold it into the graph with
`kb/harvest.py` and let `kb/project.py` carry it to the orchestrator. Do not teach code from a
notes file, and do not maintain the same fact in both places.

A raw capture is evidence — keep it. A harvested observation is superseded — the graph wins.

## Accuracy

A pitfall written down wrong is worse than none. `pitfall:A1` in the graph currently claims the
2026-08-02 Gartner application was submitted without human review; it was not (see `CLAUDE.md`).
That is what these notes exist to prevent.
