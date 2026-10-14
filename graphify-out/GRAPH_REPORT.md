# Graph Report - video-rag-with-guardrails-evals  (2026-10-14)

## Corpus Check
- 44 files · ~1,332,723 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 6, .example 1, .toml 1)

## Summary
- 491 nodes · 884 edges · 19 communities (15 shown, 4 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 27 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a9338da4`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- OutputGuardrail
- preindexer.py
- report.py
- os
- index.py
- test_session_state.py
- Video RAG with Guardrails & Evals
- transcriber.py
- src/__init__.py
- evals/__init__.py
- search.py
- logger.py
- vercel.json
- test_api.py
- cli.py
- tests/test_golden_dataset.py
- 📊 Video RAG Evaluation & Guardrail Verification Report
- test_context_precision.py

## God Nodes (most connected - your core abstractions)
1. `SessionManager` - 20 edges
2. `OutputGuardrail` - 20 edges
3. `GuardrailRouter` - 20 edges
4. `InputGuardrail` - 18 edges
5. `Video RAG with Guardrails & Evals` - 17 edges
6. `SessionState` - 16 edges
7. `execute_turn()` - 14 edges
8. `run_pipeline()` - 14 edges
9. `TranscriptChunker` - 14 edges
10. `get_searcher()` - 14 edges

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

## Communities (19 total, 4 thin omitted)

### Community 0 - "OutputGuardrail"
Cohesion: 0.07
Nodes (29): Epic 3: Runtime Guardrails ("The Bouncer"), Epic 4: Telemetry & Evaluations ("The Exam"), Epic 5: Deployment & CI, Linear Project Execution Plan: Video RAG with Guardrails & Evals, re, Runtime guardrails and safety interception pipeline., GuardrailResult, InputGuardrail (+21 more)

### Community 1 - "preindexer.py"
Cohesion: 0.27
Nodes (9): logging, build_preindexed_store(), embed_batch(), get_embedding_client(), Any, Pre-indexes video transcripts into a lightweight JSON vector store for…, Ingests all 5 session transcripts, generates embeddings, and saves a…, Returns (client_type, client) based on available API keys. (+1 more)

### Community 2 - "report.py"
Cohesion: 0.07
Nodes (41): dataclasses, json, pathlib, pytest, Multi-turn session state, conversation context management, and query…, Batch transcription script for course videos in data/videos/ using local…, subprocess, sys (+33 more)

### Community 3 - "os"
Cohesion: 0.12
Nodes (15): os, calculate_faithfulness_heuristic(), mark, MockPytest, fixture, skipif, Evaluation tests for Faithfulness metric in RAG pipelines., Heuristic calculation of statement grounding against context chunks. Used for… (+7 more)

### Community 4 - "index.py"
Cohesion: 0.10
Nodes (27): call_llm(), chat_endpoint(), ChatRequest, classify_conversational_or_meta_intent(), get_sessions(), health_check(), Any, FastAPI serverless entrypoint for Video RAG with runtime guardrails and… (+19 more)

### Community 5 - "test_session_state.py"
Cohesion: 0.06
Nodes (32): shutil, disambiguate_query(), Any, Apply sliding window pruning to respect turn and token limits., Return the dialogue history, optionally limited to the most recent turns., Return the most recent user query from history., Collect the most recently retrieved chunks across previous turns., Reset conversation history. (+24 more)

### Community 6 - "Video RAG with Guardrails & Evals"
Cohesion: 0.05
Nodes (36): 1. Input Guardrail ([`src/guardrails/input_guard.py`](file:///Users/muthukumars/Documents/workspace/video-rag-with-guardrails-evals/src/guardrails/input_guard.py)), 1. `POST /api/chat`, 1. Prerequisites, 2. Clone and Setup Environment, 2. Output Guardrail ([`src/guardrails/output_guard.py`](file:///Users/muthukumars/Documents/workspace/video-rag-with-guardrails-evals/src/guardrails/output_guard.py)), 2. `POST /api/search`, 3. Configure API Credentials, 3. `GET /api/sessions` (+28 more)

### Community 7 - "transcriber.py"
Cohesion: 0.05
Nodes (48): argparse, chromadb, chromadb_config, Epic 1: Infrastructure & Data Pipeline, dotenv, langchain_text_splitters, format_seconds_to_timestamp(), parse_timestamp_to_seconds() (+40 more)

### Community 11 - "search.py"
Cohesion: 0.13
Nodes (17): math, compute_bm25_score(), cosine_similarity(), dot_product(), load_index(), Any, Serverless in-memory vector and keyword hybrid search over pre-indexed…, Performs hybrid vector + BM25 keyword search over indexed chunks. (+9 more)

### Community 12 - "logger.py"
Cohesion: 0.07
Nodes (31): datetime, hashlib, Telemetry package initialization., get_telemetry_logger(), hash_query(), Any, Path, Structured JSON event streaming and execution telemetry logging for Video RAG. (+23 more)

### Community 13 - "vercel.json"
Cohesion: 0.50
Nodes (3): builds, routes, version

### Community 15 - "cli.py"
Cohesion: 0.05
Nodes (49): Generates a grounded answer citing video session timestamps., synthesize_rag_response(), ArgumentParser, Epic 2: Agentic RAG Core, google_adk_agents, signal, build_parser(), execute_turn() (+41 more)

### Community 17 - "tests/test_golden_dataset.py"
Cohesion: 0.20
Nodes (13): Re-export test suite for golden evaluation dataset for evals suite., dataset_items(), fixture, Tests verifying the schema, integrity, and safety of…, Verify minimum 50 items and required composition., Verify all samples conform to the required schema., Verify all non-adversarial chunk IDs exist in preindexed_embeddings.json., Verify no API keys, secrets, or sensitive credentials leaked in dataset. (+5 more)

### Community 24 - "📊 Video RAG Evaluation & Guardrail Verification Report"
Cohesion: 0.33
Nodes (5): 📂 Category Breakdown, 🎯 Executive Metric Scorecard, 🛡️ Guardrail Security Diagnostics, 🔍 Sample Evaluation Traces, 📊 Video RAG Evaluation & Guardrail Verification Report

### Community 26 - "test_context_precision.py"
Cohesion: 0.12
Nodes (14): calculate_context_precision_heuristic(), mark, MockPytest, fixture, skipif, Evaluation tests for Context Precision metric in RAG pipelines., Calculate mean average precision of relevant chunks within top retrieval…, Verify that when relevant chunks rank at the top, context precision score is… (+6 more)

## Knowledge Gaps
- **36 isolated node(s):** `version`, `builds`, `routes`, `Table of Contents`, `Executive Summary & Problem Statement` (+31 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 245 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GuardrailRouter` connect `OutputGuardrail` to `report.py`, `index.py`, `Video RAG with Guardrails & Evals`, `logger.py`, `cli.py`?**
  _High betweenness centrality (0.195) - this node is a cross-community bridge._
- **Why does `Runtime Guardrails Pipeline ("The Bouncer")` connect `Video RAG with Guardrails & Evals` to `OutputGuardrail`?**
  _High betweenness centrality (0.133) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `SessionManager` (e.g. with `execute_turn()` and `run_pipeline()`) actually correct?**
  _`SessionManager` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `OutputGuardrail` (e.g. with `Epic 3: Runtime Guardrails ("The Bouncer")` and `GuardrailResult`) actually correct?**
  _`OutputGuardrail` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `GuardrailRouter` (e.g. with `Epic 3: Runtime Guardrails ("The Bouncer")` and `Runtime Guardrails Pipeline ("The Bouncer")`) actually correct?**
  _`GuardrailRouter` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `InputGuardrail` (e.g. with `Epic 3: Runtime Guardrails ("The Bouncer")` and `GuardrailRouter`) actually correct?**
  _`InputGuardrail` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `version`, `builds`, `routes` to the rest of the system?**
  _36 weakly-connected nodes found - possible documentation gaps or missing edges._