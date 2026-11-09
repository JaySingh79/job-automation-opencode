---
name: graphrag
description: >-
  Queries the repository's Neo4j knowledge graph (built from ./ats ATS notes) with automatic
  fallback to a keyword-scored markdown scan of ./ats. Use this skill BEFORE filling a job
  application or answering ATS/process questions (e.g. Workday searchable prompt gotchas,
  Ashby React native setter, Eightfold OTP flow) to retrieve grounded file:line anchors.
---

# ATS Knowledge Graph Skill (`graphrag`)

This skill provides the Antigravity equivalent of `.opencode/tools/graphrag.ts`. It queries Neo4j (`bolt://localhost:7687`) via `.opencode/tools/graphrag_query.py` and automatically falls back to scanning `./ats/**/*.md` when Neo4j is unreachable or empty.

## Usage

Run [`src/scripts/graphrag_cli.py`](file:///D:/Projects/PRACTICE/firecrawl_test/src/scripts/graphrag_cli.py) via `uv`:

```powershell
uv run --no-project python src/scripts/graphrag_cli.py "Workday promptSearchButton flow" 5
```

### Arguments
1. `query` (string, required): Natural-language question or ATS product/topic keywords (e.g., `"Ashby resume upload"`, `"Workday searchable prompt gotchas"`, `"google forms base64 setter"`).
2. `top_k` (int, optional, default `5`): Maximum entities/documents per hop (`1` to `20`).
