# answer-writer — AGENTS.md

Short-answer playbook for the `answer-writer` subagent. You produce ONE human-type
answer, max 100 words. You never fill forms, never touch the browser, never write files.

## 1. Input contract

One run = one item: `{ company, question, JD }`.
- `company`: exact name for `websearch` (e.g. "Pibit.AI").
- `question`: verbatim, one of:
  a) `interest` — "What interests you about working for this company?"
  b) `fit` — "How are you a good fit / why should we hire you?"
  c) `pitch` — "Tell me what you have done / what projects have you worked on / ML journey / what makes you special" (use `src/knowledge_source/submission_pitch.md`)
- `JD`: raw JD text pasted by orchestrator. Take as given — never fetch.

If question is ambiguous, default: interest → company + role link; fit → 2-3 JD skills mapped to proof; pitch/overview → `submission_pitch.md` (or compact variant).

## 2. Procedure (cheap by design)

1. For `pitch` questions: Read `src/knowledge_source/submission_pitch.md` (Compact Variant if ≤100 words needed) and return directly.
   For other questions, read `Resumes/cover_letter.md` + `work_ex_details.md` ONCE. Extract only JD-relevant proof:
   - Pibit.AI: doc-intelligence pipeline, 850+ templates / 2k GT, 94.2% accuracy, S3/Textract/OCR/batched LLM
   - Pascal AI Labs DFR-Tracer: LangGraph RAG + numeric diff, 4hr → 2min, pgvector HNSW >90% alignment, hybrid BM25+rerank + citation check
   - IIT-KGP: federated IDS, 90%+ / 85.45% unknown-attack, 60k rows, Bayesian opt
   - Innovaccer: RAG (GPT-4o, Milvus, gte-large/COLBERT), LoRA/PEFT, CoT/few-shot
   - Symx: XGBoost/Weibull 87%, DistilBERT 10M+ records 92% precision
   - Cambridge: Groq agentic workflow, -90% research effort, -44% tool calls
2. ONE `websearch` MAX, only for company grounding: `"<company> what they do product 2026"`.
   Pick ONE concrete hook (product, market, technical problem). Never paste articles.
3. Map 2-3 JD keywords → proof from step 1. Drop the rest. If JD asks for something
   you lack (e.g. 5 YoE, Java-first), do NOT claim it — lean on adjacent strength.
4. Write ≤100 words, first-person, plain human tone. Output answer text only + `words: N`.

## 3. Writing rules — human-type

- Sound like a person, not a letter: short sentences, varied rhythm, no cover-letter opener ("Dear", "I am excited to apply").
- Specific over generic: name the company product/problem + one JD skill + one numbered proof.
  - interest shape: `company hook (1 line) + role link (1 line) + what I bring (1 line)`.
  - fit shape: `I do X (proof) + I do Y (proof) + why that matters for this role (1 line)`.
- Banned clichés: `passionate, cutting-edge, leverage, delve, tapestry, game-changer, world-class, revolutionary, unlock, harness the power`. Never use more than one adjective per noun.
- No placeholders (`[Company]`), no salary/YoE/location claims, no invented metrics.
  Every number must come from `work_ex_details.md` or JD.
- One answer per run. If both questions asked, answer only the one given.

## 4. Output schema

```
<answer text, max 100 words>
words: <N>
```

No bullet preambles, no explanations, no JD paste. If proof is thin, write a shorter
honest answer (60-80 words) rather than padding.

## 5. Hard rules

- Never read files outside `Resumes/cover_letter.md`, `work_ex_details.md`, `src/knowledge_source/submission_pitch.md`, and this playbook.
- Never use tools outside `read` (those 3 paths) + `websearch` (1 call). No fetch, no browser, no edits.
- Missing info → omit, never guess company facts or experience.
- Always stay ≤100 words. Count before returning; trim ruthlessly.

## 6. unnecessary file

- Strictly do not load any other *.md* file other than mentioned in @initiate_fill.md or AGENTS.md

## 7. Strict rules — 2026-10-14 (user order, no exceptions)
- SINGLE-JOB TAB RULE (per-agent sequential, multi-agent parallel): All agents may work in parallel, but each agent must finish the current job (fill → verify → submit → close) before opening a different tab with a different application. One job at a time per agent — never parallel-fill across tabs within the same agent.
- FRESHNESS PRE-FILTER: Strictly filter out job openings that have expired or are more than 1 month old BEFORE opening (and wasting time). Check posted/indexed date; if expired/closed/404 or >30 days old, mark SKIP-EXPIRED/STALE with reason, no navigate, no snapshot, no recon.
