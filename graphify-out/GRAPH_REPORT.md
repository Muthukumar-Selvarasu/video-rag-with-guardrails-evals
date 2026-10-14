# Graph Report - video-rag-with-guardrails-evals  (2026-10-14)

## Corpus Check
- 44 files · ~1,333,171 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 6, .example 1, .toml 1)

## Summary
- 493 nodes · 886 edges · 27 communities (21 shown, 6 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 27 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8af070e0`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- OutputGuardrail
- preindexer.py
- report.py
- MockPytest
- index.py
- SessionState
- Video RAG with Guardrails & Evals
- TranscriptChunker
- src/__init__.py
- evals/__init__.py
- search.py
- logger.py
- vercel.json
- test_api.py
- cli.py
- transcriber.py
- tests/test_golden_dataset.py
- SessionManager
- session.py
- ingestion/__init__.py
- test_session_state.py
- TranscriptEmbedder
- embedder.py
- 📊 Video RAG Evaluation & Guardrail Verification Report
- Any
- MockPytest

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
- `Epic 1: Infrastructure & Data Pipeline` --references--> `TranscriptEmbedder`  [INFERRED]
  docs/linear_execution_plan.md → src/ingestion/embedder.py
- `Epic 3: Runtime Guardrails ("The Bouncer")` --references--> `InputGuardrail`  [INFERRED]
  docs/linear_execution_plan.md → src/guardrails/input_guard.py
- `Epic 3: Runtime Guardrails ("The Bouncer")` --references--> `OutputGuardrail`  [INFERRED]
  docs/linear_execution_plan.md → src/guardrails/output_guard.py

## Import Cycles
- None detected.

## Communities (27 total, 6 thin omitted)

### Community 0 - "OutputGuardrail"
Cohesion: 0.06
Nodes (36): Epic 3: Runtime Guardrails ("The Bouncer"), Epic 4: Telemetry & Evaluations ("The Exam"), Epic 5: Deployment & CI, Linear Project Execution Plan: Video RAG with Guardrails & Evals, re, Runtime guardrails and safety interception pipeline., GuardrailResult, InputGuardrail (+28 more)

### Community 1 - "preindexer.py"
Cohesion: 0.31
Nodes (8): build_preindexed_store(), embed_batch(), get_embedding_client(), Any, Pre-indexes video transcripts into a lightweight JSON vector store for…, Ingests all 5 session transcripts, generates embeddings, and saves a…, Returns (client_type, client) based on available API keys., Embed a batch of text strings into 768-dimensional normalized vectors.

### Community 2 - "report.py"
Cohesion: 0.05
Nodes (52): os, pytest, get_searcher(), Singleton getter for ServerlessVectorSearch., compare_with_baseline(), evaluate_faithfulness_claim(), generate_markdown_report(), get_git_commit_sha() (+44 more)

### Community 4 - "index.py"
Cohesion: 0.10
Nodes (25): call_llm(), chat_endpoint(), ChatRequest, classify_conversational_or_meta_intent(), get_sessions(), health_check(), Any, FastAPI serverless entrypoint for Video RAG with runtime guardrails and… (+17 more)

### Community 5 - "SessionState"
Cohesion: 0.13
Nodes (10): Apply sliding window pruning to respect turn and token limits., Return the dialogue history, optionally limited to the most recent turns., Return the most recent user query from history., Reset conversation history., State management for a single multi-turn conversational session., Append a new message turn and apply sliding window truncation., Rough token count estimation based on 4 characters per token., SessionState (+2 more)

### Community 6 - "Video RAG with Guardrails & Evals"
Cohesion: 0.05
Nodes (36): 1. Input Guardrail ([`src/guardrails/input_guard.py`](file:///Users/muthukumars/Documents/workspace/video-rag-with-guardrails-evals/src/guardrails/input_guard.py)), 1. `POST /api/chat`, 1. Prerequisites, 2. Clone and Setup Environment, 2. Output Guardrail ([`src/guardrails/output_guard.py`](file:///Users/muthukumars/Documents/workspace/video-rag-with-guardrails-evals/src/guardrails/output_guard.py)), 2. `POST /api/search`, 3. Configure API Credentials, 3. `GET /api/sessions` (+28 more)

### Community 7 - "TranscriptChunker"
Cohesion: 0.12
Nodes (15): Epic 1: Infrastructure & Data Pipeline, langchain_text_splitters, format_seconds_to_timestamp(), parse_timestamp_to_seconds(), Any, Video transcript chunking with metadata and timestamp preservation., Format numeric seconds into HH:MM:SS string., Convert HH:MM:SS or MM:SS timestamp string to float seconds. (+7 more)

### Community 11 - "search.py"
Cohesion: 0.13
Nodes (18): logging, math, compute_bm25_score(), cosine_similarity(), dot_product(), load_index(), Any, Serverless in-memory vector and keyword hybrid search over pre-indexed… (+10 more)

### Community 12 - "logger.py"
Cohesion: 0.08
Nodes (29): datetime, hashlib, Telemetry package initialization., hash_query(), Any, Path, Structured JSON event streaming and execution telemetry logging for Video RAG., Create parent directory for log file if missing. (+21 more)

### Community 13 - "vercel.json"
Cohesion: 0.50
Nodes (3): builds, routes, version

### Community 15 - "cli.py"
Cohesion: 0.06
Nodes (44): Generates a grounded answer citing video session timestamps., synthesize_rag_response(), ArgumentParser, Epic 2: Agentic RAG Core, google_adk_agents, signal, build_parser(), execute_turn() (+36 more)

### Community 16 - "transcriber.py"
Cohesion: 0.16
Nodes (16): argparse, json, pathlib, main(), ChromaDB Hydration CLI and Corpus Seeding Pipeline., ingest_all(), ingest_file(), End-to-end ingestion pipeline for course video transcripts. Can ingest: -… (+8 more)

### Community 17 - "tests/test_golden_dataset.py"
Cohesion: 0.20
Nodes (13): Re-export test suite for golden evaluation dataset for evals suite., dataset_items(), fixture, Tests verifying the schema, integrity, and safety of…, Verify minimum 50 items and required composition., Verify all samples conform to the required schema., Verify all non-adversarial chunk IDs exist in preindexed_embeddings.json., Verify no API keys, secrets, or sensitive credentials leaked in dataset. (+5 more)

### Community 18 - "SessionManager"
Cohesion: 0.13
Nodes (12): Path, Registry managing active conversation sessions., Get existing session or initialize a new one., Persist session state to JSON file., Load session state from JSON file., Remove session from memory and storage., Wipe all sessions in memory., SessionManager (+4 more)

### Community 19 - "session.py"
Cohesion: 0.19
Nodes (11): dataclasses, disambiguate_query(), Multi-turn session state, conversation context management, and query…, Resolve anaphora and conversational references for follow-up queries. Args:…, Mask credentials, API keys, and sensitive PII from string., Individual dialogue message in a multi-turn conversation session., Convert message to safe dictionary with redacted content., redact_sensitive_text() (+3 more)

### Community 20 - "ingestion/__init__.py"
Cohesion: 0.26
Nodes (11): load_transcript_file(), parse_json_transcript(), parse_srt(), parse_vtt(), Any, Load and parse a transcript file (.vtt, .srt, or .json)., Transcribe an audio or video file with timestamps using Gemini Multimodal API.…, Parse WebVTT file content into timestamped cue segments. (+3 more)

### Community 21 - "test_session_state.py"
Cohesion: 0.22
Nodes (8): shutil, fixture, Unit tests for Multi-Turn Session State and Conversation Context Management., Verify SessionMessage redacts sensitive tokens and formats cleanly., Verify that messages exceeding max_tokens budget are pruned., temp_storage(), test_session_message_creation_and_redaction(), test_sliding_window_token_truncation()

### Community 22 - "TranscriptEmbedder"
Cohesion: 0.29
Nodes (5): Any, Manages embedding and indexing of transcript chunks into ChromaDB., Index a list of chunk dictionaries into ChromaDB. Args: chunks: List of…, Perform semantic similarity query against indexed transcripts., TranscriptEmbedder

### Community 23 - "embedder.py"
Cohesion: 0.33
Nodes (5): chromadb, chromadb_config, dotenv, Embedding and indexing pipeline for video transcript chunks using ChromaDB., uuid

### Community 24 - "📊 Video RAG Evaluation & Guardrail Verification Report"
Cohesion: 0.33
Nodes (5): 📂 Category Breakdown, 🎯 Executive Metric Scorecard, 🛡️ Guardrail Security Diagnostics, 🔍 Sample Evaluation Traces, 📊 Video RAG Evaluation & Guardrail Verification Report

### Community 25 - "Any"
Cohesion: 0.33
Nodes (3): Any, Collect the most recently retrieved chunks across previous turns., Export session state representation.

## Knowledge Gaps
- **36 isolated node(s):** `version`, `builds`, `routes`, `Table of Contents`, `Executive Summary & Problem Statement` (+31 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 247 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GuardrailRouter` connect `OutputGuardrail` to `index.py`, `Video RAG with Guardrails & Evals`, `cli.py`?**
  _High betweenness centrality (0.194) - this node is a cross-community bridge._
- **Why does `Runtime Guardrails Pipeline ("The Bouncer")` connect `Video RAG with Guardrails & Evals` to `OutputGuardrail`?**
  _High betweenness centrality (0.132) - this node is a cross-community bridge._
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