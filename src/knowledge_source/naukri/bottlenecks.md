# Naukri bottlenecks (3+ iteration rule — only persistent blockers listed)

- Custom `.dropArrowDD-fn` autocomplete + month/year dropdown widgets ignore synthetic events across 3 runs (2026-09-25 ×2, 2026-09-26); only working recipe: `browser_type` into #id to filter → evaluate tag matching `li` with `data-pick` → real `browser_click` on the tag.
- Save stays DISABLED with no inline errors when custom-widget state is unresolved (reproduced 3 runs); fix is real-click commits on board/medium/autocomplete — never loop-click Save, never delete user data to force it.
- Shared `playwright_browser_*` tab contention with co-agents races separate-turn select→act (2026-09-25 ×2 + 2026-09-26); re-select Naukri tab before every burst; run Naukri solo when possible.
