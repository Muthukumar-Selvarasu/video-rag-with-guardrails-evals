"""End-to-end ingestion pipeline for course video transcripts.

Can ingest:
- Existing subtitle files (.vtt, .srt, .json) in data/raw_transcripts/
- Media files (.mp4, .mov) in data/videos/ (requires GEMINI_API_KEY)
"""

import argparse
import json
import os
from pathlib import Path
from typing import List, Optional

from src.ingestion.chunker import TranscriptChunker
from src.ingestion.embedder import TranscriptEmbedder
from src.ingestion.transcriber import load_transcript_file, transcribe_media_with_gemini


def ingest_file(
    file_path: str,
    video_id: Optional[str] = None,
    title: Optional[str] = None,
    chunk_size: int = 800,
    chunk_overlap: int = 100,
) -> int:
    """Ingest a single transcript or video file into ChromaDB."""
    path = Path(file_path)
    vid_id = video_id or path.stem
    vid_title = title or path.stem.replace("_", " ").title()

    suffix = path.suffix.lower()
    print(f"[*] Processing: {path.name} (ID: {vid_id}, Title: {vid_title})")

    # Step 1: Load or Transcribe
    if suffix in (".mp4", ".mov", ".m4v", ".webm", ".mp3", ".wav"):
        print(f"[*] Transcribing media file using Gemini API...")
        segments = transcribe_media_with_gemini(str(path))
        # Save transcript to data/raw_transcripts for caching
        out_transcript = Path("data/raw_transcripts") / f"{vid_id}.json"
        out_transcript.write_text(json.dumps(segments, indent=2), encoding="utf-8")
        print(f"[✓] Saved transcript cache to {out_transcript}")
    elif suffix in (".vtt", ".srt", ".json"):
        segments = load_transcript_file(str(path))
    else:
        raise ValueError(f"Unsupported file format: {suffix}")

    print(f"[✓] Loaded {len(segments)} transcript segments/cues.")

    # Step 2: Semantic Chunking with timestamp preservation
    chunker = TranscriptChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = chunker.chunk_timestamped_segments(
        segments,
        metadata={
            "video_id": vid_id,
            "title": vid_title,
            "source_file": path.name,
        },
    )
    print(f"[✓] Generated {len(chunks)} timestamped chunks.")

    # Step 3: Embed & Store in ChromaDB
    embedder = TranscriptEmbedder()
    if embedder.collection is None:
        print("[!] Warning: ChromaDB is not installed or initialized. Chunks generated but not indexed.")
        return len(chunks)

    ids = embedder.add_chunks(chunks)
    print(f"[✓] Successfully indexed {len(ids)} chunks into ChromaDB.")
    return len(ids)


def ingest_all(
    transcripts_dir: str = "data/raw_transcripts",
    videos_dir: str = "data/videos",
) -> None:
    """Scan transcripts and videos directories and ingest all unprocessed files."""
    t_path = Path(transcripts_dir)
    v_path = Path(videos_dir)

    total_chunks = 0
    # Ingest existing transcripts first
    if t_path.exists():
        for file in t_path.glob("*.*"):
            if file.name.startswith(".") or file.suffix.lower() not in (".vtt", ".srt", ".json"):
                continue
            total_chunks += ingest_file(str(file))

    # Ingest any media files that don't have a transcript yet
    if v_path.exists():
        for file in v_path.glob("*.*"):
            if file.name.startswith(".") or file.suffix.lower() not in (
                ".mp4", ".mov", ".m4v", ".webm", ".mp3", ".wav"
            ):
                continue
            cached_transcript = t_path / f"{file.stem}.json"
            if not cached_transcript.exists():
                total_chunks += ingest_file(str(file))

    print(f"\n==========================================")
    print(f"[✓] Pipeline completed. Total chunks processed: {total_chunks}")
    print(f"==========================================")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest video transcripts into ChromaDB")
    parser.add_argument("--file", "-f", help="Path to a single transcript or media file")
    parser.add_argument("--video-id", help="Custom video ID for metadata")
    parser.add_argument("--title", help="Custom title for metadata")
    parser.add_argument(
        "--all", "-a", action="store_true", help="Ingest all files in data/raw_transcripts and data/videos"
    )

    args = parser.parse_args()

    if args.file:
        ingest_file(args.file, video_id=args.video_id, title=args.title)
    else:
        ingest_all()
