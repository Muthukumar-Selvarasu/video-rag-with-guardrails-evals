# Graph Report - video-rag-with-guardrails-evals  (2026-10-03)

## Corpus Check
- 29 files · ~1,306,187 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 6 file(s) not represented in the graph (top: (none) 5, .example 1)

## Summary
- 277 nodes · 466 edges · 15 communities (11 shown, 4 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 24 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- OutputGuardrail
- main.py
- test_api.py
- test_faithfulness.py
- index.py
- TranscriptEmbedder
- Video RAG with Guardrails & Evals
- transcriber.py
- src/__init__.py
- evals/__init__.py
- search.py
- preindexer.py
- vercel.json
- .process

## God Nodes (most connected - your core abstractions)
1. `OutputGuardrail` - 20 edges
2. `InputGuardrail` - 17 edges
3. `GuardrailRouter` - 16 edges
4. `TranscriptChunker` - 14 edges
5. `TranscriptEmbedder` - 11 edges
6. `get_searcher()` - 10 edges
7. `GuardrailResult` - 9 edges
8. `load_transcript_file()` - 9 edges
9. `format_seconds_to_timestamp()` - 8 edges
10. `run_pipeline()` - 7 edges

## Surprising Connections (you probably didn't know these)
- `Epic 2: Agentic RAG Core` --references--> `LlmAgent`  [INFERRED]
  docs/linear_execution_plan.md → src/agent/main.py
- `Epic 1: Infrastructure & Data Pipeline` --references--> `TranscriptChunker`  [INFERRED]
  docs/linear_execution_plan.md → src/ingestion/chunker.py
- `Epic 3: Runtime Guardrails ("The Bouncer")` --references--> `InputGuardrail`  [INFERRED]
  docs/linear_execution_plan.md → src/guardrails/input_guard.py
- `Key Features & Highlights` --references--> `InputGuardrail`  [INFERRED]
  README.md → src/guardrails/input_guard.py
- `Epic 3: Runtime Guardrails ("The Bouncer")` --references--> `OutputGuardrail`  [INFERRED]
  docs/linear_execution_plan.md → src/guardrails/output_guard.py

## Import Cycles
- None detected.

## Communities (15 total, 4 thin omitted)

### Community 0 - "OutputGuardrail"
Cohesion: 0.08
Nodes (25): dataclasses, Epic 3: Runtime Guardrails ("The Bouncer"), re, Key Features & Highlights, Runtime guardrails and safety interception pipeline., GuardrailResult, InputGuardrail, Input guardrails for intercepting and validating user queries. (+17 more)

### Community 1 - "main.py"
Cohesion: 0.09
Nodes (24): chromadb, chromadb_config, Epic 2: Agentic RAG Core, dotenv, google_adk_agents, os, Google ADK Agent and tool definitions., create_video_rag_agent() (+16 more)

### Community 2 - "test_api.py"
Cohesion: 0.07
Nodes (17): fastapi_testclient, pytest, calculate_context_precision_heuristic(), mark, MockPytest, fixture, skipif, Evaluation tests for Context Precision metric in RAG pipelines. (+9 more)

### Community 3 - "test_faithfulness.py"
Cohesion: 0.12
Nodes (14): calculate_faithfulness_heuristic(), mark, MockPytest, fixture, skipif, Evaluation tests for Faithfulness metric in RAG pipelines., Heuristic calculation of statement grounding against context chunks. Used for…, Verify that a faithful answer scores high grounding against retrieved… (+6 more)

### Community 4 - "index.py"
Cohesion: 0.10
Nodes (27): call_llm(), chat_endpoint(), ChatRequest, get_sessions(), health_check(), Any, FastAPI serverless entrypoint for Video RAG with runtime guardrails and…, Generates a grounded answer citing video session timestamps. (+19 more)

### Community 5 - "TranscriptEmbedder"
Cohesion: 0.12
Nodes (10): Epic 1: Infrastructure & Data Pipeline, Epic 4: Telemetry & Evaluations ("The Exam"), Epic 5: Deployment & CI, Linear Project Execution Plan: Video RAG with Guardrails & Evals, RecursiveCharacterTextSplitter, Any, Manages embedding and indexing of transcript chunks into ChromaDB., Index a list of chunk dictionaries into ChromaDB. Args: chunks: List of… (+2 more)

### Community 6 - "Video RAG with Guardrails & Evals"
Cohesion: 0.17
Nodes (11): 1. Environment Setup, 2. Configure Environment Variables, 3. Run the Web Application Locally, 4. Run Automated Tests & Evaluations, Architecture & System Workflow, Deployment to Vercel, Ingested Sessions Dataset, Knowledge Graph (+3 more)

### Community 7 - "transcriber.py"
Cohesion: 0.08
Nodes (38): argparse, json, langchain_text_splitters, pathlib, format_seconds_to_timestamp(), parse_timestamp_to_seconds(), Any, Video transcript chunking with metadata and timestamp preservation. (+30 more)

### Community 11 - "search.py"
Cohesion: 0.13
Nodes (17): math, compute_bm25_score(), cosine_similarity(), dot_product(), load_index(), Any, Serverless in-memory vector and keyword hybrid search over pre-indexed…, Performs hybrid vector + BM25 keyword search over indexed chunks. (+9 more)

### Community 12 - "preindexer.py"
Cohesion: 0.27
Nodes (9): logging, build_preindexed_store(), embed_batch(), get_embedding_client(), Any, Pre-indexes video transcripts into a lightweight JSON vector store for…, Ingests all 5 session transcripts, generates embeddings, and saves a…, Returns (client_type, client) based on available API keys. (+1 more)

### Community 13 - "vercel.json"
Cohesion: 0.50
Nodes (3): builds, routes, version

## Knowledge Gaps
- **13 isolated node(s):** `version`, `builds`, `routes`, `Architecture & System Workflow`, `Ingested Sessions Dataset` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 139 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GuardrailRouter` connect `OutputGuardrail` to `main.py`, `index.py`, `.process`?**
  _High betweenness centrality (0.118) - this node is a cross-community bridge._
- **Why does `OutputGuardrail` connect `OutputGuardrail` to `index.py`?**
  _High betweenness centrality (0.111) - this node is a cross-community bridge._
- **Why does `InputGuardrail` connect `OutputGuardrail` to `index.py`?**
  _High betweenness centrality (0.083) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `OutputGuardrail` (e.g. with `Epic 3: Runtime Guardrails ("The Bouncer")` and `Key Features & Highlights`) actually correct?**
  _`OutputGuardrail` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `InputGuardrail` (e.g. with `Epic 3: Runtime Guardrails ("The Bouncer")` and `Key Features & Highlights`) actually correct?**
  _`InputGuardrail` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `GuardrailRouter` (e.g. with `Epic 3: Runtime Guardrails ("The Bouncer")` and `Key Features & Highlights`) actually correct?**
  _`GuardrailRouter` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `TranscriptChunker` (e.g. with `Epic 1: Infrastructure & Data Pipeline` and `TestChunkerTimestamps`) actually correct?**
  _`TranscriptChunker` has 2 INFERRED edges - model-reasoned connections that need verification._