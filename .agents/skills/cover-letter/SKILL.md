---
name: cover-letter
description: >-
  Generates a customized, professionally formatted cover letter PDF from Resumes/cover_letter.md
  using src/scripts/generate_cover_letter.py and saves it to
  Resumes/cover_letter/cover_letter_<company>.pdf. Use this skill when a job application
  requests or accepts a cover letter or when invoking cover_letter_agent workflows.
---

# Cover Letter Generator Skill (`cover-letter`)

Generates a tailored cover letter PDF for a target `{company_name, job_role}` in under 3 seconds.

## Usage

Follow the playbook in [`.opencode/agents/cover_letter_agent/AGENTS.md`](file:///D:/Projects/PRACTICE/firecrawl_test/.opencode/agents/cover_letter_agent/AGENTS.md) and execute [`src/scripts/generate_cover_letter.py`](file:///D:/Projects/PRACTICE/firecrawl_test/src/scripts/generate_cover_letter.py) via `uv`:

```powershell
uv run --no-project python src/scripts/generate_cover_letter.py "<Company Name>" "<Job Role>"
```

### Output
- Writes `Resumes/cover_letter/cover_letter_<sanitized_company>.pdf`.
- Verify the file exists and has a non-zero byte count before uploading via Playwright MCP (`browser_file_upload`).
