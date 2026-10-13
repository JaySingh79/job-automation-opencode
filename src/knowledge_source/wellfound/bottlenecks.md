# Wellfound bottlenecks (3+ iteration rule — only persistent blockers listed)

- Extension-browser trusted Apply clicks always time out ("element never stable") across 3+ runs; synthetic evaluate clicks required to open the modal.
- Repeated Apply clicks in the same tab stack zombie empty modal shells (len=0, no content, no console error) — reproduced 3/3; fix: fresh tab per job + exactly one synthetic click + 8s wait; never re-click in a poisoned tab.
- Shared `playwright_browser_*` session tab contention with co-agents flips current tab mid-flow (~6 wasted calls in 2026-09-25 run, recurred 2026-09-26); burst select→act with zero interleaved calls, prefer extension tabs for Wellfound.
