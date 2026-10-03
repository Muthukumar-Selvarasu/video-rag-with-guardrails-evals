"""Serverless in-memory vector and keyword hybrid search over pre-indexed transcript chunks."""

import json
import logging
import math
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("video_search")

_INDEX_CACHE: Optional[Dict[str, Any]] = None


def load_index(index_path: str = "data/preindexed_embeddings.json") -> Dict[str, Any]:
    """Loads the preindexed vector index JSON into memory with caching."""
    global _INDEX_CACHE
    if _INDEX_CACHE is not None:
        return _INDEX_CACHE

    p = Path(index_path)
    if not p.exists():
        # Fallback search path in case running from another working directory
        alt_paths = [
            Path(__file__).parent.parent.parent / "data" / "preindexed_embeddings.json",
            Path("preindexed_embeddings.json"),
        ]
        for alt in alt_paths:
            if alt.exists():
                p = alt
                break

    if not p.exists():
        raise FileNotFoundError(f"Vector index not found at {index_path}")

    logger.info(f"Loading pre-indexed embeddings from {p}...")
    _INDEX_CACHE = json.loads(p.read_text(encoding="utf-8"))
    return _INDEX_CACHE


def dot_product(v1: List[float], v2: List[float]) -> float:
    """Compute dot product of two float lists in pure Python."""
    return sum(a * b for a, b in zip(v1, v2))


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Cosine similarity between two vectors."""
    dot = dot_product(v1, v2)
    norm1 = math.sqrt(dot_product(v1, v1)) or 1.0
    norm2 = math.sqrt(dot_product(v2, v2)) or 1.0
    return dot / (norm1 * norm2)


def tokenize(text: str) -> List[str]:
    """Tokenize text into lowercase alphanumeric keywords."""
    return re.findall(r"\b[a-zA-Z0-9_\-\.]{2,}\b", text.lower())


def compute_bm25_score(query_tokens: List[str], doc_tokens: List[str], avg_len: float = 120.0, k1: float = 1.5, b: float = 0.75) -> float:
    """Lightweight BM25 term frequency score."""
    if not query_tokens or not doc_tokens:
        return 0.0

    doc_len = len(doc_tokens)
    tf_counts: Dict[str, int] = {}
    for t in doc_tokens:
        tf_counts[t] = tf_counts.get(t, 0) + 1

    score = 0.0
    for q in query_tokens:
        tf = tf_counts.get(q, 0)
        if tf > 0:
            numerator = tf * (k1 + 1.0)
            denominator = tf + k1 * (1.0 - b + b * (doc_len / avg_len))
            score += numerator / denominator

    return score


class ServerlessVectorSearch:
    """Fast, in-memory semantic & hybrid search engine for transcript chunks."""

    def __init__(self, index_path: str = "data/preindexed_embeddings.json"):
        self.data = load_index(index_path)
        self.chunks = self.data.get("chunks", [])
        self.sessions = self.data.get("sessions", [])

        # Pre-tokenize docs for ultra-fast lexical ranking
        self.doc_tokens = [tokenize(c["text"]) for c in self.chunks]
        total_tokens = sum(len(dt) for dt in self.doc_tokens)
        self.avg_doc_len = total_tokens / max(1, len(self.doc_tokens))

    def get_query_embedding(self, query: str) -> Optional[List[float]]:
        """Compute query embedding using available API key."""
        gemini_key = os.getenv("GEMINI_API_KEY", "")
        openai_key = os.getenv("OPENAI_API_KEY", "")

        if gemini_key.startswith("AIza"):
            try:
                from google import genai
                client = genai.Client(api_key=gemini_key)
                res = client.models.embed_content(
                    model="text-embedding-004",
                    contents=query,
                )
                return res.embedding.values
            except Exception as e:
                logger.warning(f"Gemini query embedding failed: {e}")

        active_openai_key = openai_key or (gemini_key if gemini_key.startswith("sk-") else "")
        if active_openai_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=active_openai_key)
                res = client.embeddings.create(
                    model="text-embedding-3-small",
                    input=[query],
                    dimensions=768,
                )
                return res.data[0].embedding
            except Exception as e:
                logger.warning(f"OpenAI query embedding failed: {e}")

        return None

    def search(
        self,
        query: str,
        top_k: int = 4,
        session_filter: Optional[str] = None,
        min_score: float = 0.0,
    ) -> List[Dict[str, Any]]:
        """Performs hybrid vector + BM25 keyword search over indexed chunks."""
        q_tokens = tokenize(query)
        q_emb = self.get_query_embedding(query)

        results: List[Tuple[float, Dict[str, Any]]] = []

        max_bm25 = 1.0
        bm25_scores = []
        for dt in self.doc_tokens:
            s = compute_bm25_score(q_tokens, dt, avg_len=self.avg_doc_len)
            bm25_scores.append(s)
            if s > max_bm25:
                max_bm25 = s

        for idx, chunk in enumerate(self.chunks):
            # Optional session filter
            if session_filter and chunk.get("video_id") != session_filter:
                continue

            bm25_norm = bm25_scores[idx] / max_bm25 if max_bm25 > 0 else 0.0

            if q_emb is not None and "embedding" in chunk:
                # Cosine similarity
                dense_sim = cosine_similarity(q_emb, chunk["embedding"])
                # Hybrid fusion: 75% vector similarity + 25% keyword match
                final_score = 0.75 * dense_sim + 0.25 * bm25_norm
            else:
                # Lexical only fallback
                final_score = bm25_norm

            if final_score >= min_score:
                item = {
                    "id": chunk.get("id"),
                    "video_id": chunk.get("video_id"),
                    "session_num": chunk.get("session_num", 1),
                    "title": chunk.get("title"),
                    "chunk_index": chunk.get("chunk_index"),
                    "start_time": chunk.get("start_time"),
                    "end_time": chunk.get("end_time"),
                    "start_seconds": chunk.get("start_seconds", 0.0),
                    "end_seconds": chunk.get("end_seconds", 0.0),
                    "text": chunk.get("text"),
                    "score": round(final_score, 4),
                }
                results.append((final_score, item))

        results.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in results[:top_k]]


_SEARCHER: Optional[ServerlessVectorSearch] = None


def get_searcher() -> ServerlessVectorSearch:
    """Singleton getter for ServerlessVectorSearch."""
    global _SEARCHER
    if _SEARCHER is None:
        _SEARCHER = ServerlessVectorSearch()
    return _SEARCHER
