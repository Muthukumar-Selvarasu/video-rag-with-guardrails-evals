"""Unit tests for the standalone Agent CLI & REPL interface."""

import subprocess
import sys
import pytest
from src.agent.cli import build_parser, execute_turn
from src.agent.session import SessionManager


def test_cli_argument_parsing():
    """Verify parser flags and defaults."""
    parser = build_parser()

    args_default = parser.parse_args([])
    assert args_default.session is None
    assert args_default.top_k == 4
    assert args_default.verbose is False
    assert args_default.query is None

    args_custom = parser.parse_args([
        "--session", "my_session",
        "--top-k", "7",
        "--verbose",
        "--query", "What is MCP?",
    ])
    assert args_custom.session == "my_session"
    assert args_custom.top_k == 7
    assert args_custom.verbose is True
    assert args_custom.query == "What is MCP?"


def test_cli_execute_turn_non_interactive():
    """Verify single-turn execution through CLI helper function."""
    mgr = SessionManager()
    res = execute_turn(
        query="What is covered in Session 1 of Claude Code?",
        session_id="test_cli_turn",
        session_manager=mgr,
        top_k=2,
        verbose=False,
    )
    assert res.get("success") is True
    assert "response" in res
    assert len(res.get("retrieved_chunks", [])) == 2
    assert res.get("turn_count") == 2


def test_cli_subprocess_invocation():
    """Verify executing python -m src.agent.cli as a standalone subprocess."""
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.agent.cli",
            "--query",
            "Who are the instructors in Session 1?",
            "--top-k",
            "2",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert proc.returncode == 0
    assert "Agent Response:" in proc.stdout
