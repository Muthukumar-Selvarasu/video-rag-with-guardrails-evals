"""Pre-indexes video transcripts into a lightweight JSON vector store for serverless deployment."""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from src.ingestion.chunker import TranscriptChunker

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")
logger = logging.getLogger("preindexer")

SESSION_METADATA = {
    "claude-code-session-1": {
        "id": "claude-code-session-1",
        "session_num": 1,
        "title": "Session 1: Foundations & Architecture of Claude Code",
        "speakers": ["Hamza Farooq", "Ash Faria"],
        "description": "Introduction to Claude Code, foundational concepts, CLI setup, and architecture.",
    },
    "claude-code-session-2": {
        "id": "claude-code-session-2",
        "session_num": 2,
        "title": "Session 2: CLI Workflows & Context Engineering",
        "speakers": ["Hamza Farooq", "Ash Faria"],
        "description": "Module 2 covering deep CLI interaction patterns, prompt engineering, and context management.",
    },
    "claude-code-session-3": {
        "id": "claude-code-session-3",
        "session_num": 3,
        "title": "Session 3: Agentic Tool Use & Multi-File Refactoring",
        "speakers": ["Hamza Farooq", "Ash Faria"],
        "description": "Module 3 exploring tool execution, agentic refactoring, and multi-file workflows.",
    },
    "claude-code-session-4": {
        "id": "claude-code-session-4",
        "session_num": 4,
        "title": "Session 4: Production Audits & Testing Automation",
        "speakers": ["Hamza Farooq", "Ash Faria"],
        "description": "Deep-dive into accessibility audits, multi-task verification, and testing automation.",
    },
    "claude-code-session-5": {
        "id": "claude-code-session-5",
        "session_num": 5,
        "title": "Session 5: Advanced Systems & Technical Deep Dive",
        "speakers": ["Hamza Farooq"],
        "description": "Advanced technical deep-dive into custom extensions, tool design, and production agent patterns.",
    },
}


def get_embedding_client():
    """Returns (client_type, client) based on available API keys."""
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    openai_key = os.getenv("OPENAI_API_KEY", "")

    # Check for Gemini key
    if gemini_key.startswith("AIza"):
        try:
            from google import genai
            return "gemini", genai.Client(api_key=gemini_key)
        except Exception as e:
            logger.warning(f"Could not init Gemini client: {e}")

    # Fallback to OpenAI key (or OpenAI key stored in GEMINI_API_KEY)
    active_openai_key = openai_key or (gemini_key if gemini_key.startswith("sk-") else "")
    if active_openai_key:
        try:
            from openai import OpenAI
            return "openai", OpenAI(api_key=active_openai_key)
        except Exception as e:
            logger.warning(f"Could not init OpenAI client: {e}")

    return "mock", None


def embed_batch(texts: List[str], client_type: str, client: Any, dimensions: int = 768) -> List[List[float]]:
    """Embed a batch of text strings into 768-dimensional normalized vectors."""
    if client_type == "gemini":
        try:
            # Google GenAI text-embedding-004
            embeddings = []
            for text in texts:
                res = client.models.embed_content(
                    model="text-embedding-004",
                    contents=text,
                )
                embeddings.append(res.embedding.values)
            return embeddings
        except Exception as e:
            logger.error(f"Gemini embedding error: {e}")
            raise

    elif client_type == "openai":
        try:
            # OpenAI text-embedding-3-small with 768 dimensions
            res = client.embeddings.create(
                model="text-embedding-3-small",
                input=texts,
                dimensions=dimensions,
            )
            return [item.embedding for item in res.data]
        except Exception as e:
            logger.error(f"OpenAI embedding error: {e}")
            raise

    else:
        # Fallback pseudo-random normalized embedding for zero-key test environments
        import hashlib
        import math
        embeddings = []
        for text in texts:
            vec = []
            for i in range(dimensions):
                h = hashlib.sha256(f"{text}_{i}".encode("utf-8")).digest()
                val = (int.from_bytes(h[:4], "big") / (2**32)) * 2 - 1
                vec.append(val)
            norm = math.sqrt(sum(x * x for x in vec)) or 1.0
            embeddings.append([round(x / norm, 5) for x in vec])
        return embeddings


def build_preindexed_store(
    raw_dir: str = "data/raw_transcripts",
    output_file: str = "data/preindexed_embeddings.json",
    chunk_size: int = 800,
    chunk_overlap: int = 100,
    batch_size: int = 50,
) -> Dict[str, Any]:
    """Ingests all 5 session transcripts, generates embeddings, and saves a lightweight JSON index."""
    raw_path = Path(raw_dir)
    chunker = TranscriptChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    client_type, client = get_embedding_client()
    logger.info(f"Using embedding backend: {client_type}")

    all_chunks: List[Dict[str, Any]] = []
    sessions_summary: List[Dict[str, Any]] = []

    files = sorted(raw_path.glob("claude-code-session-*.json"))
    if not files:
        raise FileNotFoundError(f"No transcript files found in {raw_dir}")

    for file_path in files:
        session_id = file_path.stem
        meta_info = SESSION_METADATA.get(session_id, {
            "id": session_id,
            "session_num": int(session_id.split("-")[-1]) if session_id.split("-")[-1].isdigit() else 0,
            "title": session_id.replace("-", " ").title(),
            "speakers": ["Speaker"],
            "description": "Video session transcript",
        })

        logger.info(f"Processing transcript: {file_path.name}")
        segments = json.loads(file_path.read_text(encoding="utf-8"))
        duration = segments[-1]["end"] if segments else 0.0

        chunks = chunker.chunk_timestamped_segments(
            segments,
            metadata={
                "video_id": session_id,
                "title": meta_info["title"],
                "session_num": meta_info.get("session_num", 1),
            },
        )

        sessions_summary.append({
            **meta_info,
            "filename": file_path.name,
            "segments_count": len(segments),
            "chunks_count": len(chunks),
            "duration_seconds": duration,
            "duration_formatted": f"{int(duration // 60)}m {int(duration % 60)}s",
        })

        for i, c in enumerate(chunks):
            c_meta = c["metadata"]
            all_chunks.append({
                "id": f"{session_id}_c{i:03d}",
                "video_id": session_id,
                "title": meta_info["title"],
                "session_num": meta_info.get("session_num", 1),
                "chunk_index": i,
                "start_time": c_meta.get("start_time", "00:00"),
                "end_time": c_meta.get("end_time", "00:00"),
                "start_seconds": c_meta.get("start_seconds", 0.0),
                "end_seconds": c_meta.get("end_seconds", 0.0),
                "text": c["text"],
            })

    logger.info(f"Total chunks across 5 sessions: {len(all_chunks)}. Generating embeddings...")

    # Embed in batches
    texts = [c["text"] for c in all_chunks]
    all_embeddings: List[List[float]] = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        logger.info(f"Embedding batch {i // batch_size + 1}/{(len(texts) + batch_size - 1) // batch_size} ({len(batch)} chunks)...")
        emb_batch = embed_batch(batch, client_type, client, dimensions=768)
        # Round floats to 5 decimals to save bandwidth and memory
        all_embeddings.extend([[round(val, 5) for val in vec] for vec in emb_batch])

    for chunk, emb in zip(all_chunks, all_embeddings):
        chunk["embedding"] = emb

    store_data = {
        "model": "text-embedding-004",
        "dimensions": 768,
        "total_chunks": len(all_chunks),
        "embedding_backend": client_type,
        "sessions": sessions_summary,
        "chunks": all_chunks,
    }

    out_path = Path(output_file)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(store_data, indent=None), encoding="utf-8")
    file_size_mb = out_path.stat().st_size / (1024 * 1024)
    logger.info(f"Successfully generated vector index at {out_path} ({file_size_mb:.2f} MB, {len(all_chunks)} chunks).")

    return store_data


if __name__ == "__main__":
    build_preindexed_store()
