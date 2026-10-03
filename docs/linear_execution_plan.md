# Linear Project Execution Plan: Video RAG with Guardrails & Evals

This document defines the production delivery roadmap and sprint execution plan for **`video-rag-with-guardrails-evals`**, structured as Linear Epics and Issues.

---

## Epic 1: Infrastructure & Data Pipeline

| Issue Title | Description | Priority | Size |
| :--- | :--- | :--- | :--- |
| **Setup Project Tooling, Virtualenv & Secret Management** | Initialize Python 3.10+ virtualenv, pin dependencies in `requirements.txt` (`google-adk`, `google-genai`, `chromadb`, `ragas`, `deepeval`, `langchain-text-splitters`, `python-dotenv`), configure `.env.example`, and enforce pre-commit linting (`ruff`, `mypy`). | High | S |
| **Build Video Transcript Chunker with Timestamp Preservation** | Implement `TranscriptChunker` using `RecursiveCharacterTextSplitter` configured for chunk size (800–1200 chars) and overlap (150–200 chars). Parse `.json`, `.vtt`, and `.srt` files, retaining video IDs, titles, start/end timestamps, and chapter offsets in chunk metadata. | High | M |
| **Implement Embedding Generator with Google GenAI Embeddings** | Create `TranscriptEmbedder` utilizing Gemini `text-embedding-004` (768-dim) with client-side batching, rate-limiting retry handling, and cosine distance metric configuration in ChromaDB. | High | M |
| **Build ChromaDB Hydration CLI & Corpus Seeding Pipeline** | Build a standalone CLI script (`python -m src.ingestion.hydrate --source ./data/raw_transcripts`) to ingest, split, embed, and commit video transcripts into persistent ChromaDB storage at `./data/chroma_db` with idempotent re-indexing. | High | M |

---

## Epic 2: Agentic RAG Core

| Issue Title | Description | Priority | Size |
| :--- | :--- | :--- | :--- |
| **Develop SearchVideoTranscriptTool for ChromaDB Retrieval** | Build the custom ADK tool `SearchVideoTranscriptTool` exposing top-k semantic search, similarity score thresholding, and formatted output incorporating chunk text, video title, and timestamp ranges (`MM:SS`). | High | M |
| **Configure Google ADK LlmAgent & Gemini Model Integration** | Initialize Google ADK `LlmAgent` wired to `gemini-2.0-flash` with strict persona instructions: mandating tool invocation for factual questions, timestamp citation, and formal refusal for missing context. | High | M |
| **Implement Multi-Turn Session State & Conversation Context** | Build state management wrapper around the ADK agent to maintain conversation history, track retrieved context across turns, and avoid redundant vector queries within the same dialogue session. | Med | M |
| **Create Standalone Agent CLI & REPL Interface** | Provide an interactive terminal CLI (`python -m src.agent.cli`) allowing developers to test multi-turn queries, inspect live tool calls, and view raw retrieved transcript passages. | Low | S |

---

## Epic 3: Runtime Guardrails ("The Bouncer")

| Issue Title | Description | Priority | Size |
| :--- | :--- | :--- | :--- |
| **Author System Instructions for Strict Domain Boundaries** | Formulate and test system instructions that enforce domain boundaries: restrict answering strictly to indexed video content; prohibit general software engineering assistance, non-video queries, and competitor comparisons. | High | S |
| **Build Pre-Execution Input Interceptor for Off-Topic & Injection Blocking** | Implement `InputGuardrail` to intercept queries prior to LLM/ADK invocation. Detect prompt injection attempts (`ignore instructions`, `developer mode`) and classify domain relevance, immediately returning polite rejection responses for off-topic queries (e.g., general coding, competitors). | High | M |
| **Build Post-Execution Output Interceptor for Hallucination & Leak Prevention** | Implement `OutputGuardrail` to evaluate agent responses before returning them to users. Scan for API key/credential leakage, verify that stated facts cite valid transcript chunks, and block unsupported claims. | High | M |
| **Implement GuardrailRouter & Fallback Orchestration** | Develop `GuardrailRouter` to bind input validation, agent invocation, and output filtering into an atomic execution pipeline with structured audit logs (`stage`, `passed`, `latency_ms`). | High | M |

---

## Epic 4: Telemetry & Evaluations ("The Exam")

| Issue Title | Description | Priority | Size |
| :--- | :--- | :--- | :--- |
| **Implement ADK Telemetry Instrumentation & Execution Logging** | Instrument the ADK pipeline with OpenTelemetry / structured JSON logging to extract query text, tool arguments, retrieved context chunk IDs, token consumption, and end-to-end execution latencies. | Med | M |
| **Curate Golden Evaluation Dataset for Video RAG** | Assemble a 50+ item golden evaluation dataset (`data/eval_golden_dataset.json`) containing diverse video queries, target ground truth answers, relevant chunk IDs, and synthetic adversarial/out-of-scope prompts. | High | M |
| **Implement Automated Context Precision Evaluation Suite** | Configure RAGAS / DeepEval test suite to evaluate Context Precision: measure whether retrieved video chunks prioritize relevant content over distractor text across the golden dataset. | High | M |
| **Implement Automated Faithfulness Evaluation Suite** | Configure RAGAS / DeepEval test suite to evaluate Faithfulness: measure factual consistency of generated answers against retrieved transcript chunks to detect subtle hallucinations. | High | M |
| **Build Eval Report Generator & Trend Dashboard** | Create a script (`python -m tests.evals.report`) that outputs evaluation score summaries in Markdown and JSON formats, highlighting score regressions against baseline metrics. | Med | S |

---

## Epic 5: Deployment & CI

| Issue Title | Description | Priority | Size |
| :--- | :--- | :--- | :--- |
| **Author Comprehensive Architecture & Operational README** | Document end-to-end system architecture with Mermaid sequence diagrams, configuration guide (`.env`), ingestion runbooks, guardrail policies, and evaluation guidelines. | Med | S |
| **Implement GitHub Actions Workflow with Automated Eval Gates** | Build `.github/workflows/evals.yml` to run unit tests, linting, and automated Ragas/DeepEval suites on PRs. Enforce threshold gates (`Context Precision >= 0.80`, `Faithfulness >= 0.85`) to block regressions. | High | L |
| **Containerize Application with Docker & Cloud Run Blueprint** | Write multi-stage `Dockerfile` and deployment manifests for deploying the agent pipeline as an HTTP/gRPC service on Google Cloud Run or Vertex AI Agent Engine. | Med | M |
