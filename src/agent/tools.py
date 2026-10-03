"""Agent tools for querying and retrieving video transcripts using serverless vector search or ChromaDB."""

import os
from typing import Any, Dict, List, Optional
from src.ingestion.search import get_searcher

# Optional ChromaDB fallback
_chroma_embedder = None


def search_transcripts_structured(query: str, top_k: int = 4, session_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """Search persisted video transcripts and return structured results with metadata."""
    try:
        searcher = get_searcher()
        return searcher.search(query=query, top_k=top_k, session_filter=session_filter)
    except Exception as exc:
        # Fallback to ChromaDB if available
        global _chroma_embedder
        try:
            from src.ingestion.embedder import TranscriptEmbedder
            if _chroma_embedder is None:
                _chroma_embedder = TranscriptEmbedder()
            res = _chroma_embedder.query(query_text=query, n_results=top_k)
            docs = res.get("documents", [[]])[0]
            metas = res.get("metadatas", [[]])[0]
            structured = []
            for d, m in zip(docs, metas):
                structured.append({
                    "id": m.get("video_id", "vid"),
                    "video_id": m.get("video_id", "vid"),
                    "title": m.get("title", "Video Session"),
                    "start_time": m.get("start_time", m.get("timestamp", "00:00")),
                    "end_time": m.get("end_time", "00:00"),
                    "start_seconds": m.get("start_seconds", 0.0),
                    "end_seconds": m.get("end_seconds", 0.0),
                    "text": d,
                    "score": 1.0,
                })
            return structured
        except Exception:
            return []


def search_transcripts(query: str, top_k: int = 4) -> str:
    """Search persisted video transcripts using semantic vector search.

    Args:
        query: Search question or keywords to locate relevant video transcript segments.
        top_k: Number of most relevant transcript segments to retrieve (default: 4).

    Returns:
        Formatted string containing retrieved transcript segments with metadata and timestamps.
    """
    try:
        results = search_transcripts_structured(query=query, top_k=top_k)
        if not results:
            return "No matching video transcripts found for the given query."

        formatted_outputs = []
        for i, item in enumerate(results, start=1):
            source = item.get("title", item.get("video_id", "Video Session"))
            start_ts = item.get("start_time", "00:00")
            end_ts = item.get("end_time", "")
            time_display = f"{start_ts} - {end_ts}" if end_ts else start_ts
            formatted_outputs.append(
                f"[Result {i}] Source: {source} | Timestamp: {time_display}\n{item.get('text', '')}\n"
            )

        return "\n---\n".join(formatted_outputs)
    except Exception as exc:
        return f"Error executing transcript search: {str(exc)}"
