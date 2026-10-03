"""Video and audio transcription and subtitle parsing utility.

Supports:
- WebVTT (.vtt) file parsing
- SubRip (.srt) file parsing
- Structured JSON transcript parsing
- Multimodal audio/video transcription using Gemini API (google-genai)
"""

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def parse_vtt(content: str) -> List[Dict[str, Any]]:
    """Parse WebVTT file content into timestamped cue segments."""
    segments = []
    # Standard WebVTT cue time pattern: 00:01:23.456 --> 00:01:28.910
    cue_pattern = re.compile(
        r"((?:\d{2}:)?\d{2}:\d{2}[\.,]\d{3})\s*-->\s*((?:\d{2}:)?\d{2}:\d{2}[\.,]\d{3})"
    )

    lines = content.strip().splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        match = cue_pattern.search(line)
        if match:
            start_str, end_str = match.groups()
            cue_text_lines = []
            i += 1
            while i < len(lines) and lines[i].strip():
                cue_text_lines.append(lines[i].strip())
                i += 1
            text = " ".join(cue_text_lines)
            if text:
                segments.append({
                    "start_time": start_str,
                    "end_time": end_str,
                    "text": text,
                })
        i += 1
    return segments


def parse_srt(content: str) -> List[Dict[str, Any]]:
    """Parse SubRip (.srt) subtitle content into timestamped cue segments."""
    segments = []
    # Standard SRT cue time pattern: 00:01:23,456 --> 00:01:28,910
    srt_pattern = re.compile(
        r"(\d{2}:\d{2}:\d{2}[\.,]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[\.,]\d{3})"
    )

    blocks = re.split(r"\n\s*\n", content.strip())
    for block in blocks:
        lines = [l.strip() for l in block.strip().splitlines() if l.strip()]
        for idx, line in enumerate(lines):
            match = srt_pattern.search(line)
            if match:
                start_str, end_str = match.groups()
                text = " ".join(lines[idx + 1 :])
                if text:
                    segments.append({
                        "start_time": start_str,
                        "end_time": end_str,
                        "text": text,
                    })
                break
    return segments


def parse_json_transcript(content: str) -> List[Dict[str, Any]]:
    """Parse JSON transcript containing list of segments or cues."""
    data = json.loads(content)
    if isinstance(data, dict):
        # Look for common keys: 'segments', 'cues', 'transcript'
        for key in ("segments", "cues", "transcript", "items"):
            if key in data and isinstance(data[key], list):
                data = data[key]
                break

    if not isinstance(data, list):
        raise ValueError("JSON transcript must be a list of segments or contain a 'segments' key.")

    normalized = []
    for item in data:
        if not isinstance(item, dict):
            continue
        text = item.get("text", item.get("content", "")).strip()
        start = item.get("start", item.get("start_time", item.get("start_seconds", 0.0)))
        end = item.get("end", item.get("end_time", item.get("end_seconds", None)))
        if text:
            normalized.append({
                "start": start,
                "end": end,
                "text": text,
            })
    return normalized


def load_transcript_file(file_path: str) -> List[Dict[str, Any]]:
    """Load and parse a transcript file (.vtt, .srt, or .json)."""
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Transcript file not found: {file_path}")

    content = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()

    if suffix == ".vtt":
        return parse_vtt(content)
    elif suffix == ".srt":
        return parse_srt(content)
    elif suffix == ".json":
        return parse_json_transcript(content)
    else:
        # Default fallback: treat as plain text if no cue timestamps
        return [{"start": 0.0, "end": 0.0, "text": content.strip()}]


def transcribe_media_with_gemini(
    media_path: str,
    api_key: Optional[str] = None,
    model_name: str = "gemini-2.5-flash",
) -> List[Dict[str, Any]]:
    """Transcribe an audio or video file with timestamps using Gemini Multimodal API.

    Requires google-genai or google-generativeai and GEMINI_API_KEY.
    """
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        raise ValueError("GEMINI_API_KEY is required to transcribe media files.")

    try:
        from google import genai
        client = genai.Client(api_key=key)

        # Upload file to Gemini Files API
        uploaded_file = client.files.upload(file=media_path)

        prompt = (
            "Generate an accurate timestamped transcript of this lecture. "
            "Return ONLY a valid JSON array of objects with the following format:\n"
            "[\n"
            '  {"start_time": "00:00:00", "end_time": "00:00:15", "text": "spoken words..."}\n'
            "]\n"
            "Do not include any Markdown fencing or other text outside the JSON array."
        )

        response = client.models.generate_content(
            model=model_name,
            contents=[uploaded_file, prompt],
        )

        resp_text = response.text.strip()
        # Clean potential markdown block
        if resp_text.startswith("```"):
            resp_text = re.sub(r"^```(?:json)?\s*", "", resp_text)
            resp_text = re.sub(r"\s*```$", "", resp_text)

        return parse_json_transcript(resp_text)
    except ImportError:
        raise RuntimeError("google-genai is not installed. Run: pip install google-genai")


def transcribe_media_with_whisper(
    media_path: str,
    model_size: str = "base",
    device: str = "cpu",
    compute_type: str = "int8",
) -> List[Dict[str, Any]]:
    """Transcribe an audio or video file with timestamps using local faster-whisper.

    Args:
        media_path: Path to video or audio file (.mp4, .mov, etc.)
        model_size: Whisper model size ("tiny", "base", "small", "medium").
                    Default is "base" which provides an optimal balance of speed and accuracy.
        device: Device to run on ("cpu").
        compute_type: Quantization ("int8" for fast execution on Apple Silicon).

    Returns:
        List of segment dictionaries with start, end, and text.
    """
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        raise RuntimeError("faster-whisper is not installed. Run: pip install faster-whisper")

    # Compatibility fix: PyAV removed 'metadata_errors' parameter in recent versions
    try:
        import av
        if not getattr(av, "_patched_metadata_errors", False):
            _orig_av_open = av.open

            def _safe_av_open(*args, **kwargs):
                kwargs.pop("metadata_errors", None)
                return _orig_av_open(*args, **kwargs)

            av.open = _safe_av_open
            av._patched_metadata_errors = True
    except ImportError:
        pass

    from src.ingestion.chunker import format_seconds_to_timestamp

    print(f"[*] Loading local Whisper model '{model_size}'...")
    model = WhisperModel(model_size, device=device, compute_type=compute_type)

    print(f"[*] Transcribing {media_path}...")
    segments_generator, info = model.transcribe(media_path, beam_size=5, vad_filter=True)

    print(f"[✓] Detected language '{info.language}' ({info.language_probability:.2f})")

    results = []
    for segment in segments_generator:
        results.append({
            "start": round(segment.start, 2),
            "end": round(segment.end, 2),
            "start_time": format_seconds_to_timestamp(segment.start),
            "end_time": format_seconds_to_timestamp(segment.end),
            "text": segment.text.strip(),
        })
    return results

