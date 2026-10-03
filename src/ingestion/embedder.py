"""Embedding and indexing pipeline for video transcript chunks using ChromaDB."""

import os
import uuid
from typing import Any, Dict, List, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    chromadb = None  # type: ignore
    Settings = None  # type: ignore


class TranscriptEmbedder:
    """Manages embedding and indexing of transcript chunks into ChromaDB."""

    def __init__(
        self,
        persist_directory: Optional[str] = None,
        collection_name: Optional[str] = None,
    ):
        self.persist_directory = persist_directory or os.getenv(
            "CHROMA_PERSIST_DIR", "./data/chroma_db"
        )
        self.collection_name = collection_name or os.getenv(
            "CHROMA_COLLECTION_NAME", "video_transcripts"
        )

        # Ensure persistence directory exists
        os.makedirs(self.persist_directory, exist_ok=True)

        if chromadb is not None:
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(anonymized_telemetry=False) if Settings else None,
            )
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
        else:
            self.client = None
            self.collection = None

    def add_chunks(self, chunks: List[Dict[str, Any]]) -> List[str]:
        """Index a list of chunk dictionaries into ChromaDB.

        Args:
            chunks: List of dictionaries with 'text' and 'metadata'.

        Returns:
            List of generated document IDs.
        """
        if not chunks:
            return []

        if not self.collection:
            raise RuntimeError("ChromaDB is not installed. Please run: pip install chromadb")

        documents = [c["text"] for c in chunks]
        metadatas = [c.get("metadata", {}) for c in chunks]
        ids = [
            f"{m.get('video_id', 'vid')}_{m.get('chunk_index', uuid.uuid4().hex[:8])}"
            for m in metadatas
        ]

        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
        )
        return ids

    def query(self, query_text: str, n_results: int = 4) -> Dict[str, Any]:
        """Perform semantic similarity query against indexed transcripts."""
        if not self.collection:
            raise RuntimeError("ChromaDB is not installed. Please run: pip install chromadb")

        return self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
        )
