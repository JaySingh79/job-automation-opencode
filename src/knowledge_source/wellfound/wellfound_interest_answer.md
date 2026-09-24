# Wellfound "What interests you about working for this company?" — human answer bank
Saved: 2026-09-12. All lines are factual (Pascal / Pibit / Symx / Innovaccer / Cambridge only). Never invent.
Fill [Company], [Role], [focus] per job. Keep 3-5 sentences. Vary wording so answers are not identical.

## Variant A — Agentic / RAG roles (default)
Interested in the [Role] role at [Company] focused on [focus, e.g. LangGraph agents, RAG and evals]. At Pascal AI Labs I built DFR-Tracer, a LangGraph-based RAG agent that detects SEC 10-K restatements, with pgvector fuzzy matching and a citation-verification loop, cutting audit time from ~4 hours to under 2 minutes. At Pibit AI I shipped a document classification pipeline to 94.2% accuracy with retrieval and LLM parsing. Excited to bring that to production-grade agentic systems with memory, tool use and evals at [Company].

## Variant B — ML systems / eval roles
Interested in the [Role] role working on [focus, e.g. inference pipelines, model eval and retrieval]. At Pibit AI I built classification infrastructure with benchmarking and error analysis to 94.2%, and at Pascal AI Labs I ran vector-embedding alignment at over 90% with pgvector HNSW. At Symx AI I shipped Weibull+XGBoost ensembles at 87% failure prediction and DistilBERT pipelines at 92% precision. Strong fit for evaluation, error analysis and vector search work at [Company].

## Variant C — Healthcare / legal / high-stakes domain roles
Interested in [Company]'s [Role] role because [domain, e.g. grounded clinical assistants / citation-traced legal answers] is exactly where being wrong has consequences. At Innovaccer I worked on Sara AI NLP semantics and built RAG over GPT-4o with Milvus and multi-vector embeddings; at Pibit AI I handled corrupt and OCR-heavy PDFs with Azure/Textract confidence thresholding. At Pascal AI Labs I added hallucination rejection so every explanation passes citation verification. I want to build that kind of grounded system at [Company].

## Variant D — Junior / build-and-learn roles (with built-note: what broke / differently)
Interested in [Company]'s [Role] because it ships to production in weeks with evals, not demos. Something I built: DFR-Tracer, a LangGraph RAG agent for SEC restatements. What broke: cross-year metric renames broke joins and the LLM hallucinated footnote citations. Fix: embedding-based schema alignment plus hybrid BM25+rerank extraction with a verification loop. Differently: I would add golden-dataset eval harnesses from day one, which matches this role's build-eval-ship loop.

## Rules
- Always keep company + role names specific (never generic "your company").
- 1-2 concrete numbers max (94.2%, 87%, 92%, 4hr-to-2min, 90% alignment, 85.45% IDS).
- Never claim: voice/TTS/ASR shipped, MCTS, pentest exploits, YoE beyond 18 months total.
- If job needs a skill you lack (e.g. TTS/ASR, offensive security), say so by omission: frame around adjacent strengths, do not claim the missing skill.
