"""Batch transcription script for course videos in data/videos/ using local faster-whisper."""

import argparse
import json
import time
from pathlib import Path
from src.ingestion.transcriber import transcribe_media_with_whisper


def transcribe_videos(
    videos_dir: str = "data/videos",
    output_dir: str = "data/raw_transcripts",
    model_size: str = "base",
    force: bool = False,
) -> None:
    v_path = Path(videos_dir)
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    video_files = sorted(
        [
            f
            for f in v_path.glob("*.*")
            if f.suffix.lower() in (".mp4", ".mov", ".m4v", ".webm", ".mkv")
            and not f.name.startswith(".")
        ]
    )

    if not video_files:
        print(f"[!] No video files found in '{videos_dir}'.")
        return

    print(f"\n{'='*60}")
    print("🎬 Course Video Local Transcription Pipeline")
    print(f"Model: {model_size} | Total videos: {len(video_files)}")
    print(f"{'='*60}\n")

    start_total_time = time.time()

    for idx, video_file in enumerate(video_files, start=1):
        vid_id = video_file.stem
        target_json = out_path / f"{vid_id}.json"

        print(f"\n[{idx}/{len(video_files)}] Processing: {video_file.name}")

        if target_json.exists() and not force:
            print(f"  ↪ [SKIPPED] Transcript already exists at: {target_json}")
            print("     (Pass --force to overwrite)")
            continue

        vid_start = time.time()
        try:
            segments = transcribe_media_with_whisper(
                str(video_file),
                model_size=model_size,
            )

            # Save timestamped transcript to data/raw_transcripts/
            target_json.write_text(json.dumps(segments, indent=2), encoding="utf-8")
            elapsed = time.time() - vid_start
            print(f"  ✓ Extracted {len(segments)} timestamped cues in {elapsed:.1f}s")
            print(f"  ✓ Saved to: {target_json}")
        except Exception as exc:
            print(f"  ✗ Failed to transcribe {video_file.name}: {exc}")

    total_elapsed = time.time() - start_total_time
    print(f"\n{'='*60}")
    print(f"🎉 All videos processed in {total_elapsed/60:.1f} minutes!")
    print(f"Transcripts saved to: {output_dir}/")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract transcripts from videos using local Whisper")
    parser.add_argument(
        "--model",
        "-m",
        default="base",
        choices=["tiny", "base", "small", "medium"],
        help="Whisper model size (default: base)",
    )
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Force re-transcription even if JSON transcript already exists",
    )
    parser.add_argument(
        "--videos-dir",
        default="data/videos",
        help="Directory containing video files (default: data/videos)",
    )
    parser.add_argument(
        "--output-dir",
        default="data/raw_transcripts",
        help="Directory to save JSON transcripts (default: data/raw_transcripts)",
    )

    args = parser.parse_args()
    transcribe_videos(
        videos_dir=args.videos_dir,
        output_dir=args.output_dir,
        model_size=args.model,
        force=args.force,
    )
