# Graph Report - video-rag-with-guardrails-evals  (2026-10-04)

## Corpus Check
- 46 files · ~1,336,090 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 5, .example 1, .jsonl 1)

## Summary
- 492 nodes · 894 edges · 27 communities (23 shown, 4 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 27 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `541b6e48`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- InputGuardrail
- cli.py
- report.py
- test_api.py
- index.py
- SessionState
- Video RAG with Guardrails & Evals
- transcriber.py
- src/__init__.py
- evals/__init__.py
- .search
- logger.py
- vercel.json
- test_session_state.py
- SessionManager
- TelemetryLogger
- tests/test_golden_dataset.py
- OutputGuardrail
- Linear Project Execution Plan: Video RAG with Guardrails & Evals
- GuardrailRouter
- execute_turn
- redact_sensitive_event
- run_pipeline
- 📊 Video RAG Evaluation & Guardrail Verification Report
- repl_loop
- MockPytest

## God Nodes (most connected - your core abstractions)
1. `SessionManager` - 20 edges
2. `OutputGuardrail` - 20 edges
3. `GuardrailRouter` - 20 edges
4. `InputGuardrail` - 18 edges
5. `get_searcher()` - 18 edges
6. `Video RAG with Guardrails & Evals` - 17 edges
7. `SessionState` - 16 edges
8. `execute_turn()` - 14 edges
9. `run_pipeline()` - 14 edges
10. `TranscriptChunker` - 14 edges

## Surprising Connections (you probably didn't know these)
- `Epic 2: Agentic RAG Core` --references--> `LlmAgent`  [INFERRED]
  docs/linear_execution_plan.md → src/agent/main.py
- `Epic 3: Runtime Guardrails ("The Bouncer")` --references--> `InputGuardrail`  [INFERRED]
  docs/linear_execution_plan.md → src/guardrails/input_guard.py
- `Epic 3: Runtime Guardrails ("The Bouncer")` --references--> `OutputGuardrail`  [INFERRED]
  docs/linear_execution_plan.md → src/guardrails/output_guard.py
- `Runtime Guardrails Pipeline ("The Bouncer")` --references--> `GuardrailRouter`  [INFERRED]
  README.md → src/guardrails/router.py
- `Epic 1: Infrastructure & Data Pipeline` --references--> `TranscriptChunker`  [INFERRED]
  docs/linear_execution_plan.md → src/ingestion/chunker.py

## Import Cycles
- None detected.

## Communities (27 total, 4 thin omitted)

### Community 0 - "InputGuardrail"
Cohesion: 0.15
Nodes (13): dataclasses, re, Runtime guardrails and safety interception pipeline., GuardrailResult, InputGuardrail, Input guardrails for intercepting and validating user queries., Represents the outcome of a guardrail validation., Validates user prompts prior to agent execution. (+5 more)

### Community 1 - "cli.py"
Cohesion: 0.16
Nodes (17): google_adk_agents, logging, math, os, signal, Interactive CLI and REPL interface for the Video RAG Agent., Google ADK Agent and tool definitions., create_video_rag_agent() (+9 more)

### Community 2 - "report.py"
Cohesion: 0.06
Nodes (49): json, pathlib, build_and_verify_dataset(), Generates and verifies data/eval_golden_dataset.json with verified high…, main(), Script to curate data/eval_golden_dataset.json grounded in 5 Claude Code…, get_searcher(), Singleton getter for ServerlessVectorSearch. (+41 more)

### Community 3 - "test_api.py"
Cohesion: 0.07
Nodes (15): fastapi_testclient, pytest, mark, MockPytest, fixture, skipif, Evaluation tests for Faithfulness metric in RAG pipelines., Verify that a faithful answer scores high grounding against retrieved… (+7 more)

### Community 4 - "index.py"
Cohesion: 0.11
Nodes (22): call_llm(), chat_endpoint(), ChatRequest, get_sessions(), health_check(), FastAPI serverless entrypoint for Video RAG with runtime guardrails and…, Serves the rich modern Single Page Web Application., Health status and vector index statistics. (+14 more)

### Community 5 - "SessionState"
Cohesion: 0.07
Nodes (17): Path, Apply sliding window pruning to respect turn and token limits., Return the dialogue history, optionally limited to the most recent turns., Return the most recent user query from history., Collect the most recently retrieved chunks across previous turns., Reset conversation history., Export session state representation., Get existing session or initialize a new one. (+9 more)

### Community 6 - "Video RAG with Guardrails & Evals"
Cohesion: 0.05
Nodes (36): 1. Input Guardrail ([`src/guardrails/input_guard.py`](file:///Users/muthukumars/Documents/workspace/video-rag-with-guardrails-evals/src/guardrails/input_guard.py)), 1. `POST /api/chat`, 1. Prerequisites, 2. Clone and Setup Environment, 2. Output Guardrail ([`src/guardrails/output_guard.py`](file:///Users/muthukumars/Documents/workspace/video-rag-with-guardrails-evals/src/guardrails/output_guard.py)), 2. `POST /api/search`, 3. Configure API Credentials, 3. `GET /api/sessions` (+28 more)

### Community 7 - "transcriber.py"
Cohesion: 0.05
Nodes (54): argparse, chromadb, chromadb_config, dotenv, langchain_text_splitters, format_seconds_to_timestamp(), parse_timestamp_to_seconds(), Any (+46 more)

### Community 11 - ".search"
Cohesion: 0.13
Nodes (15): compute_bm25_score(), cosine_similarity(), dot_product(), load_index(), Any, Performs hybrid vector + BM25 keyword search over indexed chunks., Loads the preindexed vector index JSON into memory with caching., Compute dot product of two float lists in pure Python. (+7 more)

### Community 12 - "logger.py"
Cohesion: 0.11
Nodes (20): datetime, hashlib, Telemetry package initialization., get_telemetry_logger(), hash_query(), Structured JSON event streaming and execution telemetry logging for Video RAG., Return the global singleton instance of TelemetryLogger., Compute deterministic SHA-256 fingerprint for a query string. (+12 more)

### Community 13 - "vercel.json"
Cohesion: 0.50
Nodes (3): builds, routes, version

### Community 14 - "test_session_state.py"
Cohesion: 0.12
Nodes (19): shutil, disambiguate_query(), Any, Resolve anaphora and conversational references for follow-up queries. Args:…, Mask credentials, API keys, and sensitive PII from string., Individual dialogue message in a multi-turn conversation session., Convert message to safe dictionary with redacted content., Append a new message turn and apply sliding window truncation. (+11 more)

### Community 15 - "SessionManager"
Cohesion: 0.12
Nodes (17): ArgumentParser, build_parser(), main(), Build command line argument parser., Registry managing active conversation sessions., Remove session from memory and storage., Wipe all sessions in memory., SessionManager (+9 more)

### Community 16 - "TelemetryLogger"
Cohesion: 0.18
Nodes (9): Any, Path, Create parent directory for log file if missing., Record and write a telemetry event to logs/telemetry.jsonl. Args: event:…, Convenience method to construct and record a telemetry event., Read recent events from disk for auditing and dashboards., Clear the telemetry log file (useful for tests)., Thread-safe structured JSON line telemetry logger. (+1 more)

### Community 17 - "tests/test_golden_dataset.py"
Cohesion: 0.20
Nodes (13): Re-export test suite for golden evaluation dataset for evals suite., dataset_items(), fixture, Tests verifying the schema, integrity, and safety of…, Verify minimum 50 items and required composition., Verify all samples conform to the required schema., Verify all non-adversarial chunk IDs exist in preindexed_embeddings.json., Verify no API keys, secrets, or sensitive credentials leaked in dataset. (+5 more)

### Community 18 - "OutputGuardrail"
Cohesion: 0.21
Nodes (6): OutputGuardrail, Compute keyword grounding ratio between response statements and retrieved…, Alias for backward compatibility., Validate agent output against leaks and real-time grounding safety criteria.…, Validates and filters model responses before returning to the user., TestOutputGuardrails

### Community 19 - "Linear Project Execution Plan: Video RAG with Guardrails & Evals"
Cohesion: 0.15
Nodes (7): Epic 1: Infrastructure & Data Pipeline, Epic 2: Agentic RAG Core, Epic 4: Telemetry & Evaluations ("The Exam"), Epic 5: Deployment & CI, Linear Project Execution Plan: Video RAG with Guardrails & Evals, LlmAgent, RecursiveCharacterTextSplitter

### Community 20 - "GuardrailRouter"
Cohesion: 0.24
Nodes (7): Epic 3: Runtime Guardrails ("The Bouncer"), GuardrailRouter, Any, Orchestrates runtime guardrail checks around agent execution., Intercept input, invoke agent executor, and intercept output. Args: query: Raw…, TestGuardrailRouter, mock_agent()

### Community 21 - "execute_turn"
Cohesion: 0.28
Nodes (9): Any, Generates a grounded answer citing video session timestamps., synthesize_rag_response(), execute_turn(), agent_executor(), Any, Format and print response to terminal., Execute a single query turn through the pipeline and return results. (+1 more)

### Community 22 - "redact_sensitive_event"
Cohesion: 0.25
Nodes (7): Mask credentials, API keys, and sensitive PII from string., Recursively mask sensitive strings in event dictionaries., Convert to sanitized dictionary representation., redact_sensitive_event(), redact_text(), Verify credentials and PII are redacted from telemetry logs., test_telemetry_redaction()

### Community 23 - "run_pipeline"
Cohesion: 0.33
Nodes (7): Any, Execute the full query pipeline protected by runtime guardrails and multi-turn…, run_pipeline(), agent_executor(), Any, Search persisted video transcripts and return structured results with metadata., search_transcripts_structured()

### Community 24 - "📊 Video RAG Evaluation & Guardrail Verification Report"
Cohesion: 0.33
Nodes (5): 📂 Category Breakdown, 🎯 Executive Metric Scorecard, 🛡️ Guardrail Security Diagnostics, 🔍 Sample Evaluation Traces, 📊 Video RAG Evaluation & Guardrail Verification Report

### Community 25 - "repl_loop"
Cohesion: 0.40
Nodes (4): format_header(), Interactive Read-Eval-Print Loop., Return welcome banner., repl_loop()

## Knowledge Gaps
- **36 isolated node(s):** `version`, `builds`, `routes`, `Table of Contents`, `Executive Summary & Problem Statement` (+31 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 244 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GuardrailRouter` connect `GuardrailRouter` to `InputGuardrail`, `cli.py`, `index.py`, `Video RAG with Guardrails & Evals`, `logger.py`, `OutputGuardrail`, `execute_turn`, `run_pipeline`?**
  _High betweenness centrality (0.194) - this node is a cross-community bridge._
- **Why does `Runtime Guardrails Pipeline ("The Bouncer")` connect `Video RAG with Guardrails & Evals` to `GuardrailRouter`?**
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