"""Interactive CLI and REPL interface for the Video RAG Agent."""

from __future__ import annotations

import argparse
import os
import signal
import sys
import uuid
from typing import Any, Dict, List, Optional

from src.agent.main import create_video_rag_agent, run_pipeline
from src.agent.session import SessionManager, disambiguate_query
from src.agent.tools import search_transcripts_structured
from src.guardrails.router import GuardrailRouter
from src.ingestion.search import get_searcher

# ANSI Terminal formatting
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def format_header() -> str:
    """Return welcome banner."""
    return f"""
{CYAN}{BOLD}======================================================================
 Claude Code Video RAG - Interactive Terminal Agent (Google ADK)
======================================================================{RESET}
Type your questions about the 5 Claude Code video lecture sessions.
Commands:
  {YELLOW}/exit{RESET} or {YELLOW}/quit{RESET}    Exit the REPL session
  {YELLOW}/session <id>{RESET}    Switch or resume a session
  {YELLOW}/history{RESET}         Display dialogue history
  {YELLOW}/clear{RESET}           Clear conversation history
  {YELLOW}/help{RESET}            Display available commands
"""


def render_response(
    result: Dict[str, Any],
    verbose: bool = False,
    retrieved_chunks: Optional[List[Dict[str, Any]]] = None,
) -> None:
    """Format and print response to terminal."""
    success = result.get("success", False)
    stage = result.get("stage", "unknown")

    if not success:
        print(f"\n{RED}{BOLD}[Blocked / Error in {stage}]{RESET} {result.get('error') or result.get('response')}\n")
        return

    print(f"\n{GREEN}{BOLD}Agent Response:{RESET}")
    print(f"{result.get('response')}\n")

    if verbose and retrieved_chunks:
        print(f"{MAGENTA}{BOLD}--- Retrieved Transcripts & Guardrail Diagnostics ---{RESET}")
        print(f"Total chunks retrieved: {len(retrieved_chunks)}")
        for idx, chunk in enumerate(retrieved_chunks, start=1):
            cid = chunk.get("id", "unknown")
            vid = chunk.get("video_id", "session")
            ts = f"{chunk.get('start_time', '00:00')} - {chunk.get('end_time', '00:00')}"
            score = chunk.get("score", 0.0)
            text_snippet = chunk.get("text", "").strip()[:180].replace("\n", " ")
            print(f"  {CYAN}[{idx}] {cid} | {vid} @ {ts} | Score: {score:.4f}{RESET}")
            print(f"      {DIM}\"{text_snippet}...\"{RESET}")

        guard_in = result.get("input_guardrail", {})
        guard_out = result.get("output_guardrail", {})
        print(f"  {YELLOW}Guardrail Verdicts:{RESET}")
        print(f"    Input Guardrail:  Passed={guard_in.get('passed', True)}")
        print(f"    Output Guardrail: Passed={guard_out.get('passed', True)} | Grounding: {guard_out.get('grounding_score', 'N/A')}")
        print(f"{MAGENTA}------------------------------------------------------{RESET}\n")


def execute_turn(
    query: str,
    session_id: str,
    session_manager: SessionManager,
    top_k: int = 4,
    verbose: bool = False,
    agent: Optional[Any] = None,
) -> Dict[str, Any]:
    """Execute a single query turn through the pipeline and return results."""
    session_state = session_manager.get_or_create(session_id)
    history = session_state.get_history()

    # Step 1: Disambiguate if multi-turn
    effective_query = disambiguate_query(query, history) if history else query
    if verbose and effective_query != query:
        print(f"{DIM}[Disambiguated follow-up query: '{effective_query}']{RESET}")

    # Step 2: Retrieve structured chunks
    searcher = get_searcher()
    retrieved_chunks = searcher.search(query=effective_query, top_k=top_k)
    chunk_ids = [c["id"] for c in retrieved_chunks if "id" in c]

    # Step 3: Run pipeline
    router = GuardrailRouter()
    from api.index import synthesize_rag_response

    def agent_executor(prompt: str) -> str:
        return synthesize_rag_response(query=prompt, chunks=retrieved_chunks)

    result = router.process(
        query=effective_query,
        agent_executor=agent_executor,
        session_id=session_id,
        retrieval_chunk_ids=chunk_ids,
    )

    # Step 4: Update session state
    session_state.add_turn(role="user", content=query)
    if result.get("success"):
        session_state.add_turn(
            role="assistant",
            content=result.get("response", ""),
            retrieved_chunks=retrieved_chunks,
        )

    result["retrieved_chunks"] = retrieved_chunks
    result["session_id"] = session_id
    result["turn_count"] = len(session_state.messages)

    render_response(result, verbose=verbose, retrieved_chunks=retrieved_chunks)
    return result


def repl_loop(
    session_id: str,
    top_k: int = 4,
    verbose: bool = False,
    storage_dir: Optional[str] = "data/sessions",
) -> None:
    """Interactive Read-Eval-Print Loop."""
    session_manager = SessionManager(storage_dir=storage_dir)
    print(format_header())
    print(f"{DIM}Active Session: {BOLD}{session_id}{RESET} (storage: {storage_dir})\n")

    def signal_handler(sig, frame):
        print(f"\n\n{YELLOW}Interrupted (Ctrl+C). Exiting session. Goodbye!{RESET}")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    while True:
        try:
            prompt_str = f"{BOLD}video-rag [{session_id}]>{RESET} "
            user_input = input(prompt_str).strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n{YELLOW}Session ended. Goodbye!{RESET}")
            break

        if not user_input:
            continue

        # Handle Slash Commands
        lower_input = user_input.lower()
        if lower_input in ("/exit", "/quit", "exit", "quit"):
            print(f"{YELLOW}Exiting Video RAG CLI. Goodbye!{RESET}")
            break

        elif lower_input == "/help":
            print(f"\n{BOLD}Available Commands:{RESET}")
            print("  /exit, /quit       Exit the CLI")
            print("  /session <id>      Switch active session identifier")
            print("  /history           Print current session dialogue history")
            print("  /clear             Clear conversation memory in current session")
            print("  /help              Display this help menu\n")
            continue

        elif lower_input.startswith("/session"):
            parts = user_input.split(maxsplit=1)
            if len(parts) > 1 and parts[1].strip():
                session_id = parts[1].strip()
                print(f"{GREEN}Switched to session: {BOLD}{session_id}{RESET}")
            else:
                print(f"Current session: {session_id}")
            continue

        elif lower_input == "/history":
            state = session_manager.get_or_create(session_id)
            print(f"\n{BOLD}Dialogue History for [{session_id}] ({len(state.messages)} turns):{RESET}")
            for idx, msg in enumerate(state.messages, start=1):
                role_color = CYAN if msg.role == "user" else GREEN
                print(f"  {idx}. {role_color}{msg.role.upper()}:{RESET} {msg.content}")
            print()
            continue

        elif lower_input == "/clear":
            state = session_manager.get_or_create(session_id)
            state.clear()
            print(f"{YELLOW}Conversation memory cleared for session [{session_id}].{RESET}\n")
            continue

        # Regular question
        try:
            execute_turn(
                query=user_input,
                session_id=session_id,
                session_manager=session_manager,
                top_k=top_k,
                verbose=verbose,
            )
        except Exception as exc:
            print(f"{RED}Error processing query:{RESET} {exc}\n")


def build_parser() -> argparse.ArgumentParser:
    """Build command line argument parser."""
    parser = argparse.ArgumentParser(
        prog="python -m src.agent.cli",
        description="Autonomous Video RAG Agent CLI & REPL Interface over 5 Claude Code sessions.",
    )
    parser.add_argument(
        "--session",
        type=str,
        default=None,
        help="Conversation session ID to save or resume state (default: autogenerated UUID)",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=4,
        help="Number of transcript chunks to retrieve per search (default: 4)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Display raw retrieved chunk metadata, similarity distances, and guardrail verdicts",
    )
    parser.add_argument(
        "--query",
        type=str,
        default=None,
        help="Execute single non-interactive query and print response without entering REPL",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Optional Gemini model override identifier",
    )
    return parser


def main() -> None:
    """CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args()

    session_id = args.session or f"session_{uuid.uuid4().hex[:8]}"

    if args.query:
        # Non-interactive execution mode
        session_manager = SessionManager()
        execute_turn(
            query=args.query,
            session_id=session_id,
            session_manager=session_manager,
            top_k=args.top_k,
            verbose=args.verbose,
        )
        return

    # Interactive REPL mode
    repl_loop(
        session_id=session_id,
        top_k=args.top_k,
        verbose=args.verbose,
    )


if __name__ == "__main__":
    main()
