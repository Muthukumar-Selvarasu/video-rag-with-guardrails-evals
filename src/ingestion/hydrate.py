"""ChromaDB Hydration CLI and Corpus Seeding Pipeline."""

import argparse
import sys
from pathlib import Path
from src.ingestion.pipeline import ingest_all, ingest_file


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ingest video transcripts into ChromaDB storage"
    )
    parser.add_argument(
        "--source",
        "-s",
        default="./data/raw_transcripts",
        help="Source directory containing raw transcripts (.json, .vtt, .srt)",
    )
    parser.add_argument(
        "--videos",
        default="./data/videos",
        help="Directory containing video files",
    )
    parser.add_argument(
        "--file",
        "-f",
        help="Optional single file to hydrate",
    )

    args = parser.parse_args()

    if args.file:
        ingest_file(args.file)
    else:
        ingest_all(transcripts_dir=args.source, videos_dir=args.videos)


if __name__ == "__main__":
    main()
