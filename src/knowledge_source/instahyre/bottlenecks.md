# Instahyre bottlenecks (3+ iteration rule — only persistent blockers listed)

- Modal detail API degrades run-wide: 9/9 job-detail titles stuck at "Hold on, loading..." (2026-09-26 run); search/list API stays healthy — retry detail load or skip detail-gating and apply from card-level recon when this hits.
- Shared `playwright_browser_*` tab contention with Wellfound/Naukri co-agents flips current tab between select and act (observed 2026-09-25 hijack + 2026-09-26 churn); same-turn select+evaluate bursts, own dedicated tab, never touch co-agent tabs.
