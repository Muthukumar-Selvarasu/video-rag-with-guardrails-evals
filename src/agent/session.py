"""Multi-turn session state, conversation context management, and query disambiguation."""

from __future__ import annotations

import json
import logging
import re
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Patterns for sensitive credentials & PII redaction
REDACTION_PATTERNS = [
    (re.compile(r"AIza[0-9A-Za-z_\-]{30,}"), "[REDACTED_GEMINI_KEY]"),
    (re.compile(r"sk-[a-zA-Z0-9]{20,}"), "[REDACTED_OPENAI_KEY]"),
    (re.compile(r"ghp_[a-zA-Z0-9]{36}"), "[REDACTED_GITHUB_TOKEN]"),
    (re.compile(r"Bearer\s+[a-zA-Z0-9._\-]+", re.IGNORECASE), "Bearer [REDACTED_TOKEN]"),
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"), "[REDACTED_EMAIL]"),
]


def redact_sensitive_text(text: str) -> str:
    """Mask credentials, API keys, and sensitive PII from string."""
    if not text:
        return ""
    sanitized = text
    for pattern, replacement in REDACTION_PATTERNS:
        sanitized = pattern.sub(replacement, sanitized)
    return sanitized


@dataclass
class SessionMessage:
    """Individual dialogue message in a multi-turn conversation session."""

    role: str  # "user" | "assistant" | "system"
    content: str
    timestamp: float = field(default_factory=time.time)
    retrieved_chunks: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to safe dictionary with redacted content."""
        return {
            "role": self.role,
            "content": redact_sensitive_text(self.content),
            "timestamp": self.timestamp,
            "retrieved_chunk_ids": [c.get("id") for c in self.retrieved_chunks if isinstance(c, dict)],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SessionMessage:
        return cls(
            role=data.get("role", "user"),
            content=data.get("content", ""),
            timestamp=data.get("timestamp", time.time()),
            retrieved_chunks=data.get("retrieved_chunks", []),
        )


class SessionState:
    """State management for a single multi-turn conversational session."""

    def __init__(
        self,
        session_id: str,
        max_turns: int = 10,
        max_tokens: int = 4000,
    ):
        self.session_id = session_id
        self.max_turns = max_turns
        self.max_tokens = max_tokens
        self.messages: List[SessionMessage] = []
        self.created_at = time.time()
        self.updated_at = self.created_at

    def add_turn(
        self,
        role: str,
        content: str,
        retrieved_chunks: Optional[List[Dict[str, Any]]] = None,
    ) -> SessionMessage:
        """Append a new message turn and apply sliding window truncation."""
        sanitized_content = redact_sensitive_text(content)
        msg = SessionMessage(
            role=role,
            content=sanitized_content,
            timestamp=time.time(),
            retrieved_chunks=retrieved_chunks or [],
        )
        self.messages.append(msg)
        self.updated_at = time.time()
        self._truncate()
        return msg

    def _estimate_tokens(self, text: str) -> int:
        """Rough token count estimation based on 4 characters per token."""
        return max(1, len(text) // 4)

    def _truncate(self) -> None:
        """Apply sliding window pruning to respect turn and token limits."""
        # Step 1: Turn-based pruning
        if len(self.messages) > self.max_turns:
            # Preserve the most recent max_turns
            self.messages = self.messages[-self.max_turns:]

        # Step 2: Token-based pruning
        total_tokens = sum(self._estimate_tokens(m.content) for m in self.messages)
        while total_tokens > self.max_tokens and len(self.messages) > 1:
            dropped = self.messages.pop(0)
            total_tokens -= self._estimate_tokens(dropped.content)

    def get_history(self, max_turns: Optional[int] = None) -> List[SessionMessage]:
        """Return the dialogue history, optionally limited to the most recent turns."""
        if max_turns is None:
            return list(self.messages)
        return list(self.messages[-max_turns:])

    def get_last_user_query(self) -> Optional[str]:
        """Return the most recent user query from history."""
        for msg in reversed(self.messages):
            if msg.role == "user":
                return msg.content
        return None

    def get_recent_retrieved_chunks(self, limit: int = 4) -> List[Dict[str, Any]]:
        """Collect the most recently retrieved chunks across previous turns."""
        collected: List[Dict[str, Any]] = []
        seen_ids = set()
        for msg in reversed(self.messages):
            for chunk in msg.retrieved_chunks:
                cid = chunk.get("id")
                if cid and cid not in seen_ids:
                    seen_ids.add(cid)
                    collected.append(chunk)
                if len(collected) >= limit:
                    return collected
        return collected

    def clear(self) -> None:
        """Reset conversation history."""
        self.messages.clear()
        self.updated_at = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """Export session state representation."""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "turn_count": len(self.messages),
            "messages": [m.to_dict() for m in self.messages],
        }


# Follow-up patterns indicating anaphoric references
ANAPHORA_PATTERNS = [
    re.compile(r"\b(what did he say next|what happened next|and then|what next)\b", re.IGNORECASE),
    re.compile(r"\b(tell me more about (that|it|them|this))\b", re.IGNORECASE),
    re.compile(r"\b(can you explain (that|it|this) (further|in detail|more)?)\b", re.IGNORECASE),
    re.compile(r"\b(how much did (it|that) cost|what was the cost of (that|it))\b", re.IGNORECASE),
    re.compile(r"\b(what was the timestamp for (that|it)|where was that mentioned)\b", re.IGNORECASE),
    re.compile(r"\b(what about (in )?session [1-5]|how about session [1-5])\b", re.IGNORECASE),
    re.compile(r"\b(why did they do that|why is that important)\b", re.IGNORECASE),
    re.compile(r"\b(can you show an example of (that|it))\b", re.IGNORECASE),
]


def disambiguate_query(
    query: str,
    history: List[SessionMessage],
    retrieved_chunks: Optional[List[Dict[str, Any]]] = None,
) -> str:
    """Resolve anaphora and conversational references for follow-up queries.

    Args:
        query: Raw follow-up query (e.g. "What did he say next?").
        history: Previous dialogue messages.
        retrieved_chunks: Chunks from previous turns if available.

    Returns:
        Expanded and contextualized query suitable for vector search.
    """
    cleaned_query = query.strip()
    if not history:
        return cleaned_query

    is_followup = any(pattern.search(cleaned_query) for pattern in ANAPHORA_PATTERNS)
    # Also treat very short queries (< 4 words) containing pronouns as follow-ups
    pronoun_match = bool(re.search(r"\b(it|that|this|they|he|she|next)\b", cleaned_query, re.IGNORECASE))
    if len(cleaned_query.split()) <= 4 and pronoun_match:
        is_followup = True

    if not is_followup:
        return cleaned_query

    # Extract topic from last user query
    last_user_query = None
    for msg in reversed(history):
        if msg.role == "user":
            last_user_query = msg.content
            break

    if not last_user_query:
        return cleaned_query

    # Extract contextual entities / subject from previous query
    # Strip common interrogative prefixes
    topic = re.sub(
        r"^(what is|what are|how does|how do|why is|explain|tell me about|who are)\s+",
        "",
        last_user_query,
        flags=re.IGNORECASE,
    ).strip("?., ")

    # Check for session reference in follow-up, e.g. "What about in session 3?"
    session_spec = re.search(r"\b(session\s*[1-5])\b", cleaned_query, re.IGNORECASE)
    if session_spec:
        session_str = session_spec.group(1)
        expanded = f"{topic} in {session_str}"
        logger.info(f"Disambiguated session cross-reference: '{query}' -> '{expanded}'")
        return expanded

    # Synthesize disambiguated query
    expanded = f"{topic} {cleaned_query}"
    logger.info(f"Disambiguated anaphoric query: '{query}' -> '{expanded}'")
    return expanded


class SessionManager:
    """Registry managing active conversation sessions."""

    def __init__(self, storage_dir: Optional[Path] = None, max_turns: int = 10, max_tokens: int = 4000):
        self.storage_dir = Path(storage_dir) if storage_dir else None
        if self.storage_dir:
            self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.max_turns = max_turns
        self.max_tokens = max_tokens
        self._sessions: Dict[str, SessionState] = {}

    def get_or_create(self, session_id: str) -> SessionState:
        """Get existing session or initialize a new one."""
        if session_id in self._sessions:
            return self._sessions[session_id]

        # Check storage if configured
        if self.storage_dir:
            persisted = self.load(session_id)
            if persisted:
                self._sessions[session_id] = persisted
                return persisted

        state = SessionState(
            session_id=session_id,
            max_turns=self.max_turns,
            max_tokens=self.max_tokens,
        )
        self._sessions[session_id] = state
        return state

    def save(self, session_id: str, path: Optional[Path] = None) -> Optional[Path]:
        """Persist session state to JSON file."""
        state = self._sessions.get(session_id)
        if not state:
            return None

        target = path or (self.storage_dir / f"{session_id}.json" if self.storage_dir else None)
        if not target:
            return None

        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(state.to_dict(), indent=2), encoding="utf-8")
        return target

    def load(self, session_id: str, path: Optional[Path] = None) -> Optional[SessionState]:
        """Load session state from JSON file."""
        target = path or (self.storage_dir / f"{session_id}.json" if self.storage_dir else None)
        if not target or not target.exists():
            return None

        try:
            data = json.loads(target.read_text(encoding="utf-8"))
            state = SessionState(
                session_id=data.get("session_id", session_id),
                max_turns=self.max_turns,
                max_tokens=self.max_tokens,
            )
            state.created_at = data.get("created_at", time.time())
            state.updated_at = data.get("updated_at", time.time())
            for m in data.get("messages", []):
                state.messages.append(SessionMessage.from_dict(m))
            self._sessions[session_id] = state
            return state
        except Exception as exc:
            logger.warning(f"Failed to load session {session_id} from {target}: {exc}")
            return None

    def delete(self, session_id: str) -> bool:
        """Remove session from memory and storage."""
        removed = self._sessions.pop(session_id, None) is not None
        if self.storage_dir:
            f = self.storage_dir / f"{session_id}.json"
            if f.exists():
                f.unlink()
                removed = True
        return removed

    def clear_all(self) -> None:
        """Wipe all sessions in memory."""
        self._sessions.clear()
