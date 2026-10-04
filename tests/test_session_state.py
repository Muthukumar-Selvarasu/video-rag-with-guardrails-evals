"""Unit tests for Multi-Turn Session State and Conversation Context Management."""

import shutil
from pathlib import Path
import pytest
from src.agent.session import (
    SessionManager,
    SessionMessage,
    SessionState,
    disambiguate_query,
    redact_sensitive_text,
)
from src.agent.main import run_pipeline


@pytest.fixture
def temp_storage(tmp_path):
    storage = tmp_path / "sessions"
    storage.mkdir(parents=True, exist_ok=True)
    yield storage
    if storage.exists():
        shutil.rmtree(storage)


def test_session_message_creation_and_redaction():
    """Verify SessionMessage redacts sensitive tokens and formats cleanly."""
    msg = SessionMessage(
        role="user",
        content="Here is my key AIzaSyD1234567890123456789012345678901 and email user@example.com",
    )
    d = msg.to_dict()
    assert "[REDACTED_GEMINI_KEY]" in d["content"]
    assert "[REDACTED_EMAIL]" in d["content"]
    assert "AIzaSyD" not in d["content"]


def test_sliding_window_turn_truncation():
    """Verify that turns exceeding max_turns are pruned in FIFO order."""
    state = SessionState(session_id="test_turns", max_turns=4)
    for i in range(8):
        state.add_turn(role="user" if i % 2 == 0 else "assistant", content=f"Turn message {i}")

    history = state.get_history()
    assert len(history) == 4
    # The last 4 messages should be 4, 5, 6, 7
    assert history[0].content == "Turn message 4"
    assert history[-1].content == "Turn message 7"


def test_sliding_window_token_truncation():
    """Verify that messages exceeding max_tokens budget are pruned."""
    state = SessionState(session_id="test_tokens", max_turns=20, max_tokens=60)
    # Add a huge message
    state.add_turn(role="user", content="A" * 200)
    # Add subsequent smaller messages
    state.add_turn(role="assistant", content="Short reply 1")
    state.add_turn(role="user", content="Short query 2")

    history = state.get_history()
    # The initial huge message should have been popped
    total_tokens = sum(state._estimate_tokens(m.content) for m in history)
    assert total_tokens <= 60 or len(history) == 1


def test_anaphora_query_disambiguation():
    """Verify follow-up queries with pronouns or continuation are disambiguated."""
    history = [
        SessionMessage(role="user", content="How does Claude Code integrate with git?"),
        SessionMessage(role="assistant", content="Claude Code runs git status and git diff..."),
    ]

    # Follow up 1: "What did he say next?"
    q1 = disambiguate_query("What did he say next?", history)
    assert "git" in q1.lower()
    assert "claude code" in q1.lower()

    # Follow up 2: "Tell me more about that"
    q2 = disambiguate_query("Tell me more about that", history)
    assert "git" in q2.lower()

    # Follow up 3: Cross-session reference "What about in session 3?"
    q3 = disambiguate_query("What about in session 3?", history)
    assert "session 3" in q3.lower()

    # Standalone query should not be modified
    standalone = "Who is the CEO of Anthropic?"
    q4 = disambiguate_query(standalone, history)
    assert q4 == standalone


def test_session_manager_persistence(temp_storage):
    """Verify session save, load, and cache lifecycle."""
    mgr = SessionManager(storage_dir=temp_storage)
    session = mgr.get_or_create("user_session_42")
    session.add_turn(role="user", content="Explain Model Context Protocol.")
    session.add_turn(role="assistant", content="MCP is an open standard for LLMs.")

    saved_path = mgr.save("user_session_42")
    assert saved_path is not None and saved_path.exists()

    # Load in a fresh manager instance
    fresh_mgr = SessionManager(storage_dir=temp_storage)
    loaded = fresh_mgr.load("user_session_42")
    assert loaded is not None
    assert loaded.session_id == "user_session_42"
    assert len(loaded.messages) == 2
    assert "Model Context Protocol" in loaded.messages[0].content


def test_run_pipeline_multi_turn_session():
    """Verify run_pipeline correctly maintains multi-turn session state."""
    mgr = SessionManager()
    session_id = "test_pipeline_multi_turn"

    # Turn 1
    res1 = run_pipeline(
        query="What are the foundations of Claude Code in Session 1?",
        session_id=session_id,
        session_manager=mgr,
    )
    assert res1.get("session_id") == session_id
    assert res1.get("turn_count") == 2

    # Turn 2: Follow-up question
    res2 = run_pipeline(
        query="What did he say next?",
        session_id=session_id,
        session_manager=mgr,
    )
    assert res2.get("session_id") == session_id
    assert res2.get("turn_count") == 4
    session = mgr.get_or_create(session_id)
    assert len(session.messages) == 4
