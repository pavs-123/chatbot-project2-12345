# RAG Types (Basic to Advanced)

This guide explains common RAG (Retrieval-Augmented Generation) patterns from beginner-friendly to more advanced. Each type has a short description, an ASCII diagram, and how to run it.

Prerequisites:
- Add your OpenAI key to a `.env` file at the repo root:
  - `OPENAI_API_KEY=sk-...`
- Install dependencies if needed:
  - `pip install -q langchain langchain-openai langchain-community chromadb python-dotenv`

Docs location and persistence:
- Sample docs live in `rag/sample_docs/` (add your own `.txt`/`.md` files)
- Chroma DB persists in `rag/chroma_db/`

Quickstart tour:
- Reingest and run all types: `python rag/types/run_all.py --reingest`
- Run one type: `python rag/types/run_all.py --type naive --query "What is RAG?"`

---

## Type 1: Naive RAG (Retrieve-then-Read)

Description:
- Retrieve top-k relevant docs for a question
- Feed docs + question to the LLM with a simple prompt
- Easiest to understand; solid baseline

ASCII Diagram:

```
Question ──► Retriever ──► Top-k Docs ──► Prompt (Context + Question) ──► LLM ──► Answer
```

Run:
- `python rag/types/run_all.py --type naive --query "What is RAG?"`
- Or direct: `python rag/types/naive.py`

Files:
- `rag/types/naive.py`

---

## Type 2: RAG + Simple Reranker

Description:
- Retrieve more docs than you need (e.g., k=6)
- Ask the LLM to briefly score each doc’s relevance (0-10)
- Reorder by score and use top documents to answer
- Improves quality when initial retrieval is noisy

ASCII Diagram:

```
Question
   │
   ├─► Retriever (k=6+) ─► Docs
   │                       │
   │                (score with LLM)
   │                       ▼
   └────────────────► Reranker ─► Top-N Docs ─► Prompt ─► LLM ─► Answer
```

Run:
- `python rag/types/run_all.py --type rerank --query "How does Chroma work?"`
- Or direct: `python rag/types/rerank.py`

Files:
- `rag/types/rerank.py`

Notes:
- This uses an LLM for a lightweight rerank. For production, consider model-based or vector-based rerankers (e.g., cross-encoders).

---

## Type 3: Multi-Query RAG

Description:
- Expand the user’s question into multiple phrasings
- Retrieve for each phrasing, then merge unique docs
- Helps cover synonyms and different angles of the question

ASCII Diagram:

```
Question ─► Query Expander (LLM) ─► {Q1, Q2, Q3}
                 │                    │    │    │
                 └────────────────────┼────┼────┘
                                      ▼    ▼
                                   Retriever for each
                                      ▼    ▼
                                   Merge & Deduplicate ─► Prompt ─► LLM ─► Answer
```

Run:
- `python rag/types/run_all.py --type multiquery --query "What are embeddings used for?"`
- Or direct: `python rag/types/multiquery.py`

Files:
- `rag/types/multiquery.py`

---

## Type 4: Map-Reduce Style RAG

Description:
- Retrieve docs
- Map: summarize each doc briefly (focused on the question)
- Reduce: combine the summaries into a concise final answer
- Helps when individual docs are long; scales better for many docs

ASCII Diagram:

```
Question ─► Retriever ─► Docs ─► Map (LLM summarize each) ─► Summaries
                                                   │
                                                   ▼
                                       Reduce (LLM combine) ─► Final Answer
```

Run:
- `python rag/types/run_all.py --type map_reduce --query "Summarize the sample docs."`
- Or direct: `python rag/types/map_reduce.py`

Files:
- `rag/types/map_reduce.py`

---

## Tips & Next Steps

- Add your own documents under `rag/sample_docs/` and reingest:
  - `python rag/types/run_all.py --reingest --type naive --query "Your question"`
- Adjust retrieval depth (top_k) via environment var:
  - `RAG_TOP_K=6`
- Swap vector store or embeddings if needed (e.g., FAISS or local embeddings)
- Consider production refinements:
  - Cited answers (include per-chunk sources)
  - Better rerankers (cross-encoder, OpenSearch k-NN w/ rescoring)
  - Structured prompts and answer templates
  - Guardrails and hallucination mitigation

If you want, I can add:
- A LangGraph version for each RAG type
- A web/CLI interactive switcher to pick a RAG type at runtime
- Unit tests that exercise each type end-to-end (skipping if no API key)
