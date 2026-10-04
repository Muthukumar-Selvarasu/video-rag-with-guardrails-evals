# Graph Report - video-rag-with-guardrails-evals  (2026-10-04)

## Corpus Check
- 30 files · ~1,319,141 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 6 file(s) not represented in the graph (top: (none) 5, .example 1)

## Summary
- 304 nodes · 498 edges · 14 communities (11 shown, 3 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 22 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `34d78d0f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- OutputGuardrail
- main.py
- os
- test_api.py
- index.py
- .add_chunks
- Video RAG with Guardrails & Evals
- transcriber.py
- src/__init__.py
- evals/__init__.py
- search.py
- preindexer.py
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
9. `ingest_file()` - 9 edges
10. `load_transcript_file()` - 9 edges

## Surprising Connections (you probably didn't know these)
- `Epic 2: Agentic RAG Core` --references--> `LlmAgent`  [INFERRED]
  docs/linear_execution_plan.md → src/agent/main.py
- `Runtime Guardrails Pipeline ("The Bouncer")` --references--> `GuardrailRouter`  [INFERRED]
  README.md → src/guardrails/router.py
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
Cohesion: 0.07
Nodes (27): dataclasses, Epic 3: Runtime Guardrails ("The Bouncer"), re, Runtime guardrails and safety interception pipeline., GuardrailResult, InputGuardrail, Input guardrails for intercepting and validating user queries., Represents the outcome of a guardrail validation. (+19 more)

### Community 1 - "main.py"
Cohesion: 0.10
Nodes (20): Epic 2: Agentic RAG Core, Epic 4: Telemetry & Evaluations ("The Exam"), Epic 5: Deployment & CI, Linear Project Execution Plan: Video RAG with Guardrails & Evals, google_adk_agents, Google ADK Agent and tool definitions., create_video_rag_agent(), LlmAgent (+12 more)

### Community 2 - "os"
Cohesion: 0.12
Nodes (15): os, calculate_context_precision_heuristic(), mark, MockPytest, fixture, skipif, Evaluation tests for Context Precision metric in RAG pipelines., Calculate mean average precision of relevant chunks within top retrieval… (+7 more)

### Community 3 - "test_api.py"
Cohesion: 0.07
Nodes (17): fastapi_testclient, pytest, calculate_faithfulness_heuristic(), mark, MockPytest, fixture, skipif, Evaluation tests for Faithfulness metric in RAG pipelines. (+9 more)

### Community 4 - "index.py"
Cohesion: 0.10
Nodes (27): call_llm(), chat_endpoint(), ChatRequest, get_sessions(), health_check(), Any, FastAPI serverless entrypoint for Video RAG with runtime guardrails and…, Generates a grounded answer citing video session timestamps. (+19 more)

### Community 5 - ".add_chunks"
Cohesion: 0.40
Nodes (3): Any, Index a list of chunk dictionaries into ChromaDB. Args: chunks: List of…, Perform semantic similarity query against indexed transcripts.

### Community 6 - "Video RAG with Guardrails & Evals"
Cohesion: 0.05
Nodes (36): 1. Input Guardrail ([`src/guardrails/input_guard.py`](file:///Users/muthukumars/Documents/workspace/video-rag-with-guardrails-evals/src/guardrails/input_guard.py)), 1. `POST /api/chat`, 1. Prerequisites, 2. Clone and Setup Environment, 2. Output Guardrail ([`src/guardrails/output_guard.py`](file:///Users/muthukumars/Documents/workspace/video-rag-with-guardrails-evals/src/guardrails/output_guard.py)), 2. `POST /api/search`, 3. Configure API Credentials, 3. `GET /api/sessions` (+28 more)

### Community 7 - "transcriber.py"
Cohesion: 0.06
Nodes (44): argparse, Epic 1: Infrastructure & Data Pipeline, json, langchain_text_splitters, pathlib, format_seconds_to_timestamp(), parse_timestamp_to_seconds(), Any (+36 more)

### Community 11 - "search.py"
Cohesion: 0.13
Nodes (17): math, compute_bm25_score(), cosine_similarity(), dot_product(), load_index(), Any, Serverless in-memory vector and keyword hybrid search over pre-indexed…, Performs hybrid vector + BM25 keyword search over indexed chunks. (+9 more)

### Community 12 - "preindexer.py"
Cohesion: 0.15
Nodes (14): chromadb, chromadb_config, dotenv, logging, Embedding and indexing pipeline for video transcript chunks using ChromaDB., build_preindexed_store(), embed_batch(), get_embedding_client() (+6 more)

### Community 13 - "vercel.json"
Cohesion: 0.50
Nodes (3): builds, routes, version

## Knowledge Gaps
- **32 isolated node(s):** `version`, `builds`, `routes`, `Table of Contents`, `Executive Summary & Problem Statement` (+27 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 158 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GuardrailRouter` connect `OutputGuardrail` to `main.py`, `index.py`, `Video RAG with Guardrails & Evals`?**
  _High betweenness centrality (0.276) - this node is a cross-community bridge._
- **Why does `Runtime Guardrails Pipeline ("The Bouncer")` connect `Video RAG with Guardrails & Evals` to `OutputGuardrail`?**
  _High betweenness centrality (0.205) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `OutputGuardrail` (e.g. with `Epic 3: Runtime Guardrails ("The Bouncer")` and `GuardrailResult`) actually correct?**
  _`OutputGuardrail` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `InputGuardrail` (e.g. with `Epic 3: Runtime Guardrails ("The Bouncer")` and `GuardrailRouter`) actually correct?**
  _`InputGuardrail` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `GuardrailRouter` (e.g. with `Epic 3: Runtime Guardrails ("The Bouncer")` and `Runtime Guardrails Pipeline ("The Bouncer")`) actually correct?**
  _`GuardrailRouter` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `TranscriptChunker` (e.g. with `Epic 1: Infrastructure & Data Pipeline` and `TestChunkerTimestamps`) actually correct?**
  _`TranscriptChunker` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `version`, `builds`, `routes` to the rest of the system?**
  _32 weakly-connected nodes found - possible documentation gaps or missing edges._