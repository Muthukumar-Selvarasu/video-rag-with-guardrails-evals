# Graph Report - video-rag-with-guardrails-evals  (2026-10-03)

## Corpus Check
- 29 files · ~1,308,296 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 6 file(s) not represented in the graph (top: (none) 5, .example 1)

## Summary
- 301 nodes · 488 edges · 14 communities (11 shown, 3 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 22 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- OutputGuardrail
- main.py
- test_api.py
- test_faithfulness.py
- index.py
- TranscriptEmbedder
- Video RAG with Guardrails & Evals
- TranscriptChunker
- src/__init__.py
- evals/__init__.py
- .search
- transcriber.py
- vercel.json

## God Nodes (most connected - your core abstractions)
1. `OutputGuardrail` - 19 edges
2. `Video RAG with Guardrails & Evals` - 17 edges
3. `InputGuardrail` - 16 edges
4. `GuardrailRouter` - 16 edges
5. `TranscriptChunker` - 14 edges
6. `TranscriptEmbedder` - 11 edges
7. `get_searcher()` - 10 edges
8. `GuardrailResult` - 9 edges
9. `load_transcript_file()` - 9 edges
10. `format_seconds_to_timestamp()` - 8 edges

## Surprising Connections (you probably didn't know these)
- `Epic 2: Agentic RAG Core` --references--> `LlmAgent`  [INFERRED]
  docs/linear_execution_plan.md → src/agent/main.py
- `Epic 1: Infrastructure & Data Pipeline` --references--> `TranscriptEmbedder`  [INFERRED]
  docs/linear_execution_plan.md → src/ingestion/embedder.py
- `Epic 3: Runtime Guardrails ("The Bouncer")` --references--> `InputGuardrail`  [INFERRED]
  docs/linear_execution_plan.md → src/guardrails/input_guard.py
- `Epic 3: Runtime Guardrails ("The Bouncer")` --references--> `OutputGuardrail`  [INFERRED]
  docs/linear_execution_plan.md → src/guardrails/output_guard.py
- `Epic 3: Runtime Guardrails ("The Bouncer")` --references--> `GuardrailRouter`  [INFERRED]
  docs/linear_execution_plan.md → src/guardrails/router.py

## Import Cycles
- None detected.

## Communities (14 total, 3 thin omitted)

### Community 0 - "OutputGuardrail"
Cohesion: 0.06
Nodes (33): dataclasses, Epic 3: Runtime Guardrails ("The Bouncer"), Epic 4: Telemetry & Evaluations ("The Exam"), Epic 5: Deployment & CI, Linear Project Execution Plan: Video RAG with Guardrails & Evals, logging, 1. Input Guardrail ([`src/guardrails/input_guard.py`](file:///Users/muthukumars/Documents/workspace/video-rag-with-guardrails-evals/src/guardrails/input_guard.py)), 2. Output Guardrail ([`src/guardrails/output_guard.py`](file:///Users/muthukumars/Documents/workspace/video-rag-with-guardrails-evals/src/guardrails/output_guard.py)) (+25 more)

### Community 1 - "main.py"
Cohesion: 0.15
Nodes (13): Epic 2: Agentic RAG Core, google_adk_agents, Google ADK Agent and tool definitions., create_video_rag_agent(), LlmAgent, Any, Main entrypoint initializing the Google ADK LlmAgent for Video RAG., Initialize and configure the production Google ADK Video RAG Agent. Args:… (+5 more)

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
Cohesion: 0.20
Nodes (8): Any, Search persisted video transcripts and return structured results with metadata., search_transcripts_structured(), Any, Manages embedding and indexing of transcript chunks into ChromaDB., Index a list of chunk dictionaries into ChromaDB. Args: chunks: List of…, Perform semantic similarity query against indexed transcripts., TranscriptEmbedder

### Community 6 - "Video RAG with Guardrails & Evals"
Cohesion: 0.06
Nodes (32): 1. `POST /api/chat`, 1. Prerequisites, 2. Clone and Setup Environment, 2. `POST /api/search`, 3. Configure API Credentials, 3. `GET /api/sessions`, 4. `GET /api/health`, 4. Launch the Local Development Server (+24 more)

### Community 7 - "TranscriptChunker"
Cohesion: 0.08
Nodes (30): Epic 1: Infrastructure & Data Pipeline, langchain_text_splitters, format_seconds_to_timestamp(), parse_timestamp_to_seconds(), Any, Video transcript chunking with metadata and timestamp preservation., Format numeric seconds into HH:MM:SS string., Convert HH:MM:SS or MM:SS timestamp string to float seconds. (+22 more)

### Community 11 - ".search"
Cohesion: 0.13
Nodes (15): compute_bm25_score(), cosine_similarity(), dot_product(), load_index(), Any, Performs hybrid vector + BM25 keyword search over indexed chunks., Loads the preindexed vector index JSON into memory with caching., Compute dot product of two float lists in pure Python. (+7 more)

### Community 12 - "transcriber.py"
Cohesion: 0.09
Nodes (29): argparse, chromadb, chromadb_config, dotenv, json, math, os, pathlib (+21 more)

### Community 13 - "vercel.json"
Cohesion: 0.50
Nodes (3): builds, routes, version

## Knowledge Gaps
- **32 isolated node(s):** `version`, `builds`, `routes`, `Table of Contents`, `Executive Summary & Problem Statement` (+27 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 158 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GuardrailRouter` connect `OutputGuardrail` to `main.py`, `index.py`?**
  _High betweenness centrality (0.279) - this node is a cross-community bridge._
- **Why does `Runtime Guardrails Pipeline ("The Bouncer")` connect `OutputGuardrail` to `Video RAG with Guardrails & Evals`?**
  _High betweenness centrality (0.207) - this node is a cross-community bridge._
- **Why does `Video RAG with Guardrails & Evals` connect `Video RAG with Guardrails & Evals` to `OutputGuardrail`?**
  _High betweenness centrality (0.195) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `OutputGuardrail` (e.g. with `Epic 3: Runtime Guardrails ("The Bouncer")` and `GuardrailResult`) actually correct?**
  _`OutputGuardrail` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `InputGuardrail` (e.g. with `Epic 3: Runtime Guardrails ("The Bouncer")` and `GuardrailRouter`) actually correct?**
  _`InputGuardrail` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `GuardrailRouter` (e.g. with `Epic 3: Runtime Guardrails ("The Bouncer")` and `Runtime Guardrails Pipeline ("The Bouncer")`) actually correct?**
  _`GuardrailRouter` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `TranscriptChunker` (e.g. with `Epic 1: Infrastructure & Data Pipeline` and `TestChunkerTimestamps`) actually correct?**
  _`TranscriptChunker` has 2 INFERRED edges - model-reasoned connections that need verification._