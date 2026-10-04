"""Structured JSON event streaming and execution telemetry logging for Video RAG."""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import threading
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Default file path for structured telemetry
DEFAULT_LOG_PATH = Path("logs/telemetry.jsonl")

# Patterns for sensitive credentials & PII redaction
REDACTION_PATTERNS = [
    (re.compile(r"AIza[0-9A-Za-z_\-]{30,}"), "[REDACTED_GEMINI_KEY]"),
    (re.compile(r"sk-[a-zA-Z0-9]{20,}"), "[REDACTED_OPENAI_KEY]"),
    (re.compile(r"ghp_[a-zA-Z0-9]{36}"), "[REDACTED_GITHUB_TOKEN]"),
    (re.compile(r"Bearer\s+[a-zA-Z0-9._\-]+", re.IGNORECASE), "Bearer [REDACTED_TOKEN]"),
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"), "[REDACTED_EMAIL]"),
    (re.compile(r"\b\d{3}[-.\s]??\d{3}[-.\s]??\d{4}\b"), "[REDACTED_PHONE]"),
]


def redact_text(text: str) -> str:
    """Mask credentials, API keys, and sensitive PII from string."""
    if not text:
        return ""
    sanitized = text
    for pattern, replacement in REDACTION_PATTERNS:
        sanitized = pattern.sub(replacement, sanitized)
    return sanitized


def redact_sensitive_event(data: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively mask sensitive strings in event dictionaries."""
    sanitized = {}
    for key, value in data.items():
        if isinstance(value, str):
            sanitized[key] = redact_text(value)
        elif isinstance(value, dict):
            sanitized[key] = redact_sensitive_event(value)
        elif isinstance(value, list):
            sanitized[key] = [
                redact_text(v) if isinstance(v, str)
                else redact_sensitive_event(v) if isinstance(v, dict)
                else v
                for v in value
            ]
        else:
            sanitized[key] = value
    return sanitized


def hash_query(query: str) -> str:
    """Compute deterministic SHA-256 fingerprint for a query string."""
    normalized = query.strip().lower()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


@dataclass
class TelemetryEvent:
    """Standardized schema for execution telemetry events."""

    timestamp_iso: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    )
    session_id: str = "default_session"
    query_hash: str = ""
    input_guard_passed: bool = True
    retrieval_chunk_ids: List[str] = field(default_factory=list)
    retrieval_latency_ms: float = 0.0
    llm_latency_ms: float = 0.0
    output_guard_passed: bool = True
    grounding_score: float = 0.0
    total_duration_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to sanitized dictionary representation."""
        data = asdict(self)
        return redact_sensitive_event(data)


class TelemetryLogger:
    """Thread-safe structured JSON line telemetry logger."""

    _instance: Optional[TelemetryLogger] = None
    _lock = threading.Lock()

    def __init__(self, log_path: Optional[Path] = None):
        self.log_path = Path(log_path or os.getenv("TELEMETRY_LOG_PATH", DEFAULT_LOG_PATH))
        self._file_lock = threading.Lock()
        self._ensure_log_directory()

    def _ensure_log_directory(self) -> None:
        """Create parent directory for log file if missing."""
        try:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            logger.warning(f"Could not create telemetry log directory {self.log_path.parent}: {exc}")

    def log(self, event: TelemetryEvent) -> Dict[str, Any]:
        """Record and write a telemetry event to logs/telemetry.jsonl.

        Args:
            event: TelemetryEvent instance.

        Returns:
            Sanitized dictionary written to disk.
        """
        event_dict = event.to_dict()
        line = json.dumps(event_dict, ensure_ascii=False) + "\n"

        with self._file_lock:
            try:
                self._ensure_log_directory()
                with open(self.log_path, "a", encoding="utf-8") as f:
                    f.write(line)
            except Exception as exc:
                logger.error(f"Failed to write telemetry event to {self.log_path}: {exc}")

        return event_dict

    def log_interaction(
        self,
        session_id: str,
        query: str,
        input_guard_passed: bool,
        retrieval_chunk_ids: List[str],
        retrieval_latency_ms: float,
        llm_latency_ms: float,
        output_guard_passed: bool,
        grounding_score: float,
        total_duration_ms: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Convenience method to construct and record a telemetry event."""
        event = TelemetryEvent(
            session_id=session_id or "default_session",
            query_hash=hash_query(query),
            input_guard_passed=input_guard_passed,
            retrieval_chunk_ids=retrieval_chunk_ids or [],
            retrieval_latency_ms=round(retrieval_latency_ms, 2),
            llm_latency_ms=round(llm_latency_ms, 2),
            output_guard_passed=output_guard_passed,
            grounding_score=round(grounding_score, 4),
            total_duration_ms=round(total_duration_ms, 2),
            metadata=metadata or {},
        )
        return self.log(event)

    def read_recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Read recent events from disk for auditing and dashboards."""
        if not self.log_path.exists():
            return []

        events = []
        with self._file_lock:
            try:
                with open(self.log_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                events.append(json.loads(line))
                            except json.JSONDecodeError:
                                continue
            except Exception as exc:
                logger.error(f"Failed reading telemetry events from {self.log_path}: {exc}")

        return events[-limit:]

    def clear(self) -> None:
        """Clear the telemetry log file (useful for tests)."""
        with self._file_lock:
            if self.log_path.exists():
                self.log_path.write_text("", encoding="utf-8")


def get_telemetry_logger(log_path: Optional[Path] = None) -> TelemetryLogger:
    """Return the global singleton instance of TelemetryLogger."""
    with TelemetryLogger._lock:
        if TelemetryLogger._instance is None or log_path is not None:
            TelemetryLogger._instance = TelemetryLogger(log_path=log_path)
        return TelemetryLogger._instance
