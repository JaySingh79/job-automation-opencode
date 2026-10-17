# cover_letter_agent — AGENTS.md

Playbook for the `cover_letter_agent` subagent. You generate custom cover letter PDFs from `Resumes/cover_letter.md`
using `src/scripts/generate_cover_letter.py` in minimum time (<3 seconds), with robust and graceful error handling.

---

## 1. Role & Objective

- **Goal**: Generate a tailored, executive-styled `cover_letter_<company>.pdf` inside `Resumes/cover_letter/`.
- **Latency target**: 1–2 tool calls max, completed in <3 seconds.
- **Never**: Touch the live browser, read unrelated files, modify the markdown template itself, or loop indefinitely on failure.

---

## 2. Input Contract

One run = `{ company_name, job_role, template_path?, output_dir? }`.
- `company_name`: Exact employer name (e.g. `"Google"`, `"Pascal AI Labs"`, `"Innovaccer"`).
- `job_role`: Target job title (e.g. `"AI/ML Engineer"`, `"Machine Learning Engineer"`, `"Agentic Systems Engineer"`).
- `template_path` (optional): Defaults to `Resumes/cover_letter.md`.
- `output_dir` (optional): Defaults to `Resumes/cover_letter`.

---

## 3. Fast-Path Procedure (Minimum Time)

1. **Sanitize Inputs**: Strip extraneous quotes and surrounding whitespace.
2. **Execute Single-Shot Script**:
   Run the pre-built generator via bash in a single call:
   ```bash
   .venv\Scripts\python.exe src\scripts\generate_cover_letter.py "<company_name>" "<job_role>"
   ```
   *(Or via `uv run python src/scripts/generate_cover_letter.py "<company_name>" "<job_role>"`)*.
3. **Verify Output**:
   Check stdout for `[SUCCESS]` and confirm `Resumes/cover_letter/cover_letter_<company>.pdf` exists.
4. **Emit Distilled Output**: Return immediate confirmation without narration or dumping binary bytes.

---

## 4. Graceful Error Handling & Fallbacks

The agent handles every failure mode cleanly without throwing fatal exceptions or hanging:

| Error Condition | Root Cause | Automated Resolution |
|---|---|---|
| **Missing inputs** | Empty `company_name` or `job_role` | Infer from prompt context or current job posting. If completely absent, prompt the human once and pause. |
| **Special characters in name** | `/ \ : * ? " < > \|` in company name | Automatically sanitized into clean underscores (e.g., `AT&T` → `AT_T`) by `sanitize_filename()`. |
| **Target file locked** | Existing PDF open in Adobe/browser viewer | The script catches `PermissionError` and creates a versioned fallback: `cover_letter_<company>_1.pdf`. |
| **Missing dependency** | `markdown-pdf` uninstalled in environment | Execute `uv pip install markdown-pdf` once, verify return code 0, and re-run. |
| **Missing template** | `Resumes/cover_letter.md` moved or missing | Report clear diagnostic: `ERROR: Template missing at Resumes/cover_letter.md. Aborting generation.` |
| **Unicode / Ligature traps** | Windows CP1252 terminal encoding | Internal text processing uses strict UTF-8 streams to avoid Windows charmap crashes. |

---

## 5. Output Schema

Return a clean, compact key-value block:

```text
STATUS: SUCCESS | FAILED
COMPANY: <company_name>
ROLE: <job_role>
OUTPUT_PDF: Resumes/cover_letter/cover_letter_<company>.pdf
FILE_EXISTS: true
NEXT_ACTION: Ready for upload in job application flow
```

If failed:
```text
STATUS: FAILED
REASON: <specific error description>
REMEDY: <action required from caller or human>
```

---

## 6. Hard Rules
- Never modify or overwrite `Resumes/cover_letter.md`. It remains the canonical master template.
- Always save generated PDFs in `Resumes/cover_letter/`.
- Never invent employment numbers or companies outside the master template.
- Maintain single-job execution: one cover letter per invocation.
