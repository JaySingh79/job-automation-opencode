Pascal AI Labs | ML Intern

• Architected and built DFR-Tracer, an AI-powered forensic reconciliation engine that automatically detects and explains financial restatements across SEC 10-K filings
• Combining deterministic numerical diff analysis with a LangGraph-based RAG agent, reducing manual analyst audit time from ~4 hours per company to under 2 minutes per query.
• Engineered a fuzzy schema alignment pipeline using vector embeddings and pgvector HNSW indexing to resolve cross-year metric name inconsistencies with >90% alignment accuracy, paired with a bitemporal fact lineage graph that traces multi-hop restatement chains across 7+ years of historical filings.
• Designed and deployed a citation-validated footnote extraction system using Gemini 3.0 Flash with hybrid BM25 + semantic reranking and a hallucination rejection loop, delivering source-cited restatement explanations that pass programmatic citation verification — eliminating the "black box" problem of conventional financial LLM tools.

Pibit AI (YC W21) | AI Intern (Research)

• Built a loss run document page classification pipeline as a crucial middleware step of a multi-agentic lossrun extraction system.
• Combining regex-nlp based LLM extraction parsing, IDF inverted-index retrieval, dependency-chain reasoning. 
• Created 850+ template labels, 2k+ GT using page mono/bigram inline key pairs to uniquely identify page-layout variants.
• Built an Streamlit application for graph-clustering deduplication/keyword search/comparison of GT configuration JSONs
• Achieved an accuracy of 80% with below 10% of GT addition, with final accuracy reaching 94.2% over entire template addition and bulk testing results.
• Built Global PDF Handler for corrupt/blur/masked/cropped/incomplete/password protected ingestions.
• S3 based document retrieval with Textract enabled page rotation, and batched IOT/COT LLM document parsing with minimal token consumption / per document.
• Detected page continuation through regex parsing of LLM-extracted page number text over sectional count.
• Integrated Azure/Textract OCR confidence thresholding, and analytics design for detecting unreadable docs.

Symx AI | Data Scientist

• Predictive Maintenance: Built Weibull regression + XGBoost ensemble models achieving 87% failure prediction accuracy, reducing maintenance costs by 14% and downtime by 50% across global mining operations.​

• NLP Intelligence: Developed DistilBERT-based pipeline processing 10M+ maintenance records with LDA topic modeling, achieving 92% precision in automated spare parts forecasting for X.Parts platform.​

• Fleet Optimization: Implemented genetic algorithms + Deep Q-Networks for operations optimization, achieving 9% fuel reduction (100K liters saved annually per truck)

Innovaccer | Data Science Intern

- Worked on the natural language semantics of "Sara’s", AI model of Innovaccer, with a progression from NLTK to transformer based architecture, as part of Innovaccer’s NLP R&D team.
- Explored open-source models like GTR-T5 base, Flan-T5 XL, and others. Fine-tuned models over single, multi-GPU processing for optimization, for refined outputs and low computation time, respectively.
- Leveraged LangChain and diverse prompt engineering techniques, including Chain of Thought, Zero-shot, and Few-shot learning leading to high precision results.
- Built a RAG pipeline over gpt 4o, Milvus as the vector database, and gte-large, COLBERT for generating multi-vector embedding for high precision, fast retrieval.
- Built a unified asynchronous model chaining and dividing the multiple task focused model on top of lexical similarity architecture.

Cambridge Judge Business School | Research Associate

- Developed an AI-driven Startup Portal using Groq API, delivering personalized strategies, business ideas, and enhanced user engagement
- Engineered NLP techniques for extracting key insights from inputs, generating SWOT analyses, boosting decision-making efficiency by 40%.
● Built a DAG-based agentic workflow that reduced research effort by 90% and generated 10+ business ideas.
● Designed a shared agent memory layer for coordinated reasoning across research tasks cutting tool calls by 44%.
● Curated agent execution through parallel task scheduling and response caching, reducing inference cost, latency.
- Integrated prompt engineering, enabling context-aware output, addressing marketing strategies, financial planning, resource optimization