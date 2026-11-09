---
name: google-search
description: >-
  Executes paginated Google searches via SerpApi (up to 50 deduplicated results per call)
  matching OpenCode's google_search tool. Use this skill as the first-preference search tool
  whenever searching for job postings using src/search_guidance/search_hack.md keywords or
  whenever a playbook calls for google_search.
---

# Google Search Skill (SerpApi)

This skill provides the Antigravity equivalent of `.opencode/tools/google_search.ts`. It queries SerpApi's Google engine using `SERPAPI_API_KEY` (or `SERP_API_KEY`) from `.env` and returns deduplicated `{title, link, snippet}` JSON results.

## Usage

Run [`src/scripts/serpapi_search.py`](file:///D:/Projects/PRACTICE/firecrawl_test/src/scripts/serpapi_search.py) via `uv`:

```powershell
uv run --no-project python src/scripts/serpapi_search.py --query "(site:boards.greenhouse.io OR site:jobs.lever.co OR site:ashbyhq.com) (\"Machine Learning\" OR \"AI\") \"India\"" --num-pages 5 --gl us --hl en
```

### Arguments
- `--query` / `-q`: Google search query string (supports Boolean operators, `site:`, `after:`, quotes).
- `--num-pages` / `-n`: Number of pages to fetch (`1` to `5`, 10 results per page; default `5` = up to 50 results).
- `--gl`: Geolocation code (default `"us"`, use `"in"` for India-specific SERP ranking when needed).
- `--hl`: Host language (default `"en"`).
- `--google-domain`: Google domain (default `"google.com"`).

## Job Search Workflow
1. Read [`src/search_guidance/search_hack.md`](file:///D:/Projects/PRACTICE/firecrawl_test/src/search_guidance/search_hack.md) to construct targeted ATS Boolean queries.
2. Execute `uv run --no-project python src/scripts/serpapi_search.py` with the query.
3. Filter out non-India (unless remote), Java/C++-only, senior, or `> 2` YoE roles, and save fresher roles to `src/job_search_results/<subfolder>/` (e.g. `ashby_lever_greenhouse/`, `google_dork_sweeps/`, `wellfound/`).
