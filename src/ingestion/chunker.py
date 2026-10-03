"""Video transcript chunking with metadata and timestamp preservation."""

from typing import Any, Dict, List, Optional

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    class RecursiveCharacterTextSplitter:  # type: ignore
        def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 150, separators: Optional[List[str]] = None):
            self.chunk_size = chunk_size
            self.chunk_overlap = chunk_overlap

        def split_text(self, text: str) -> List[str]:
            step = max(1, self.chunk_size - self.chunk_overlap)
            return [text[i : i + self.chunk_size] for i in range(0, len(text), step)]


def format_seconds_to_timestamp(seconds: float) -> str:
    """Format numeric seconds into HH:MM:SS string."""
    seconds = max(0.0, float(seconds))
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def parse_timestamp_to_seconds(ts: str) -> float:
    """Convert HH:MM:SS or MM:SS timestamp string to float seconds."""
    parts = ts.strip().replace(",", ".").split(":")
    try:
        if len(parts) == 3:
            return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
        elif len(parts) == 2:
            return float(parts[0]) * 60 + float(parts[1])
        elif len(parts) == 1:
            return float(parts[0])
    except (ValueError, TypeError):
        pass
    return 0.0


class TranscriptChunker:
    """Splits raw video transcripts into semantic chunks while maintaining metadata."""

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 150,
        separators: Optional[List[str]] = None,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators or ["\n\n", "\n", ". ", " ", ""],
        )

    def chunk_transcript(
        self, text: str, metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Split raw text into chunks with associated metadata.

        Args:
            text: Raw transcript text content.
            metadata: Base metadata dictionary (e.g., video_id, title, url).

        Returns:
            List of dictionaries containing chunk text and updated metadata.
        """
        base_meta = metadata or {}
        raw_splits = self.splitter.split_text(text)

        chunks: List[Dict[str, Any]] = []
        for idx, chunk in enumerate(raw_splits):
            chunk_meta = {
                **base_meta,
                "chunk_index": idx,
                "total_chunks": len(raw_splits),
                "char_length": len(chunk),
            }
            chunks.append({"text": chunk, "metadata": chunk_meta})

        return chunks

    def chunk_timestamped_segments(
        self,
        segments: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Group timestamped transcript segments (cues) into semantic chunks.

        Each chunk retains start and end timestamps so video players can seek
        directly to the relevant segment.

        Args:
            segments: List of segment dicts with keys 'text', 'start' (or 'start_time'),
                      and optional 'end' (or 'end_time').
            metadata: Base metadata (e.g. video_id, title, url).

        Returns:
            List of chunks with aggregated text and calculated timestamp metadata.
        """
        base_meta = metadata or {}
        if not segments:
            return []

        chunks: List[Dict[str, Any]] = []
        current_texts: List[str] = []
        current_char_count = 0
        current_start_sec: Optional[float] = None
        current_end_sec: Optional[float] = None

        for seg in segments:
            seg_text = seg.get("text", "").strip()
            if not seg_text:
                continue

            # Determine start and end seconds for this segment
            raw_start = seg.get("start", seg.get("start_seconds", seg.get("start_time", 0.0)))
            start_sec = (
                parse_timestamp_to_seconds(str(raw_start))
                if isinstance(raw_start, str)
                else float(raw_start)
            )

            raw_end = seg.get("end", seg.get("end_seconds", seg.get("end_time", start_sec + 5.0)))
            end_sec = (
                parse_timestamp_to_seconds(str(raw_end))
                if isinstance(raw_end, str)
                else float(raw_end)
            )

            if current_start_sec is None:
                current_start_sec = start_sec

            # Check if adding this segment exceeds chunk_size
            if current_texts and (current_char_count + len(seg_text) + 1 > self.chunk_size):
                chunk_body = " ".join(current_texts)
                chunk_meta = {
                    **base_meta,
                    "chunk_index": len(chunks),
                    "start_seconds": current_start_sec,
                    "end_seconds": current_end_sec or current_start_sec,
                    "start_time": format_seconds_to_timestamp(current_start_sec),
                    "end_time": format_seconds_to_timestamp(current_end_sec or current_start_sec),
                    "timestamp": format_seconds_to_timestamp(current_start_sec),
                    "char_length": len(chunk_body),
                }
                chunks.append({"text": chunk_body, "metadata": chunk_meta})

                # Reset buffer with overlap if desired
                current_texts = [seg_text]
                current_char_count = len(seg_text)
                current_start_sec = start_sec
                current_end_sec = end_sec
            else:
                current_texts.append(seg_text)
                current_char_count += len(seg_text) + 1
                current_end_sec = end_sec

        # Flush remaining buffer
        if current_texts:
            chunk_body = " ".join(current_texts)
            chunk_meta = {
                **base_meta,
                "chunk_index": len(chunks),
                "start_seconds": current_start_sec or 0.0,
                "end_seconds": current_end_sec or 0.0,
                "start_time": format_seconds_to_timestamp(current_start_sec or 0.0),
                "end_time": format_seconds_to_timestamp(current_end_sec or 0.0),
                "timestamp": format_seconds_to_timestamp(current_start_sec or 0.0),
                "char_length": len(chunk_body),
            }
            chunks.append({"text": chunk_body, "metadata": chunk_meta})

        # Update total_chunks across all generated chunks
        for c in chunks:
            c["metadata"]["total_chunks"] = len(chunks)

        return chunks

