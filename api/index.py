"""FastAPI serverless entrypoint for Video RAG with runtime guardrails and evaluation inspector."""

import json
import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

from src.guardrails.input_guard import InputGuardrail
from src.guardrails.output_guard import OutputGuardrail
from src.guardrails.router import GuardrailRouter
from src.ingestion.search import get_searcher

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")
logger = logging.getLogger("video_rag_api")

app = FastAPI(
    title="Claude Code Video RAG API",
    description="Serverless Video RAG over 5 Claude Code sessions with runtime guardrails",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Guardrails
input_guard = InputGuardrail(
    course_keywords=[
        "claude", "code", "agent", "prompt", "context", "terminal", "cli",
        "tool", "bash", "mcp", "subagent", "test", "audit", "refactor",
        "video", "session", "lecture", "module", "model", "token", "git",
    ],
    enforce_course_relevance=False,  # Use regex filters to prevent false rejections while blocking off-topic
)
output_guard = OutputGuardrail(min_grounding_score=0.15)
guardrail_router = GuardrailRouter(input_guard=input_guard, output_guard=output_guard)


class ChatRequest(BaseModel):
    message: str = Field(..., description="User query or question")
    session_id: Optional[str] = Field(None, description="Optional session filter (e.g. claude-code-session-1)")
    top_k: Optional[int] = Field(4, description="Number of transcript chunks to retrieve")


class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 4
    session_filter: Optional[str] = None


def call_llm(system_prompt: str, user_prompt: str) -> str:
    """Invokes available LLM (Gemini or OpenAI) with fallback to extractive synthesis."""
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    openai_key = os.getenv("OPENAI_API_KEY", "")

    # Try Gemini if AIza key is present
    if gemini_key.startswith("AIza"):
        try:
            from google import genai
            client = genai.Client(api_key=gemini_key)
            model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
            response = client.models.generate_content(
                model=model_name,
                contents=f"{system_prompt}\n\nUser Question: {user_prompt}",
            )
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            logger.warning(f"Gemini LLM call failed: {e}")

    # Try OpenAI if active key is present
    active_openai_key = openai_key or (gemini_key if gemini_key.startswith("sk-") else "")
    if active_openai_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=active_openai_key)
            model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            resp = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
                max_tokens=650,
            )
            if resp.choices and resp.choices[0].message.content:
                return resp.choices[0].message.content.strip()
        except Exception as e:
            logger.warning(f"OpenAI LLM call failed: {e}")

    return ""


def synthesize_rag_response(query: str, chunks: List[Dict[str, Any]]) -> str:
    """Generates a grounded answer citing video session timestamps."""
    if not chunks:
        return "Based on the available video transcripts, I cannot find information to answer this question."

    context_lines = []
    for c in chunks:
        sid = c.get("video_id", "session")
        st = c.get("start_time", "00:00")
        et = c.get("end_time", "")
        time_str = f"{st} - {et}" if et else st
        context_lines.append(f"[{sid} @ {time_str}]: \"{c.get('text', '')}\"")

    context_str = "\n\n".join(context_lines)

    system_prompt = (
        "You are an expert AI teaching assistant for the 5 Claude Code video lecture sessions. "
        "Strict Instructions:\n"
        "1. Answer the user query factually based ONLY on the provided video transcript segments.\n"
        "2. Directly cite the video session and timestamp in your response, e.g. [claude-code-session-2 @ 56:10] or [04:12].\n"
        "3. Highlight key concepts (CLI commands, tool use, subagent workflows, config files).\n"
        "4. If the retrieved transcripts do not contain enough information to answer, state: "
        "'Based on the available video transcripts, I cannot find information to answer this question.'\n"
        "5. Keep the answer clear, concise, and structured with bullet points where appropriate."
    )

    user_prompt = f"Video Transcript Context:\n{context_str}\n\nQuestion: {query}"

    llm_output = call_llm(system_prompt, user_prompt)
    if llm_output:
        return llm_output

    # Deterministic fallback synthesis if no external API is reachable
    top_chunk = chunks[0]
    sid = top_chunk.get("video_id", "claude-code-session")
    time_str = top_chunk.get("start_time", "00:00")
    fallback_resp = (
        f"Based on [{sid} @ {time_str}], the discussion highlights: \"{top_chunk.get('text', '')[:250]}...\"\n\n"
        f"Additional context from [{chunks[-1].get('video_id', sid)} @ {chunks[-1].get('start_time', '00:00')}]: "
        f"\"{chunks[-1].get('text', '')[:200]}...\""
    )
    return fallback_resp


@app.get("/", response_class=HTMLResponse)
async def serve_index():
    """Serves the rich modern Single Page Web Application."""
    # Look for templates/index.html in root or relative to api/
    candidates = [
        Path("templates/index.html"),
        Path(__file__).parent.parent / "templates" / "index.html",
        Path(__file__).parent / "templates" / "index.html",
    ]
    for p in candidates:
        if p.exists():
            return HTMLResponse(content=p.read_text(encoding="utf-8"))

    # Minimal fallback HTML if template file is missing
    return HTMLResponse(
        content="""<!DOCTYPE html><html><body><h1>Claude Code Video RAG</h1><p>Please ensure templates/index.html is installed.</p></body></html>"""
    )


@app.get("/api/health")
async def health_check():
    """Health status and vector index statistics."""
    try:
        searcher = get_searcher()
        return {
            "status": "healthy",
            "model": "text-embedding-004",
            "total_chunks": len(searcher.chunks),
            "total_sessions": len(searcher.sessions),
            "guardrails": ["InputGuardrail", "OutputGuardrail", "GuardrailRouter"],
        }
    except Exception as e:
        return {"status": "degraded", "error": str(e)}


@app.get("/api/sessions")
async def get_sessions():
    """Returns metadata for all 5 Claude Code video lecture sessions."""
    try:
        searcher = get_searcher()
        return {
            "success": True,
            "sessions": searcher.sessions,
            "total_chunks": len(searcher.chunks),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/search")
async def search_endpoint(req: SearchRequest):
    """Direct transcript search endpoint."""
    searcher = get_searcher()
    results = searcher.search(
        query=req.query,
        top_k=req.top_k or 4,
        session_filter=req.session_filter,
    )
    return {"success": True, "count": len(results), "results": results}


@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    """Protected RAG query endpoint guarded by GuardrailRouter."""
    query = req.message.strip()

    # Step 1: Input Guardrail Check
    input_result = input_guard.validate(query)
    if not input_result.passed:
        logger.warning(f"Input rejected by guardrail: {input_result.reason}")
        return {
            "success": False,
            "error": input_result.reason,
            "response": f"Request blocked: {input_result.reason}",
            "stage": "input_guardrail",
            "guardrails": {
                "input": {
                    "passed": False,
                    "reason": input_result.reason,
                    "details": input_result.details,
                },
                "output": None,
            },
            "sources": [],
        }

    # Step 2: Semantic Transcript Retrieval
    # Auto-detect session mention if not explicitly filtered
    session_filter = req.session_id
    if not session_filter:
        session_match = re.search(r"\bsession\s*([1-5])\b", query, re.IGNORECASE)
        if session_match:
            session_filter = f"claude-code-session-{session_match.group(1)}"

    searcher = get_searcher()
    retrieved_chunks = searcher.search(
        query=query,
        top_k=req.top_k or 5,
        session_filter=session_filter,
    )

    combined_context = " ".join([c.get("text", "") for c in retrieved_chunks])

    # Step 3: LLM Generation
    try:
        raw_response = synthesize_rag_response(query=query, chunks=retrieved_chunks)
    except Exception as exc:
        logger.error(f"Response synthesis failed: {exc}", exc_info=True)
        return {
            "success": False,
            "error": str(exc),
            "response": "An error occurred while generating response.",
            "stage": "agent_execution",
            "guardrails": {
                "input": {"passed": True, "reason": None, "details": input_result.details},
                "output": None,
            },
            "sources": [],
        }

    # Step 4: Output Guardrail Check (Credential Leaks & Context Grounding)
    output_result = output_guard.validate(raw_response, context=combined_context)
    if not output_result.passed:
        logger.warning(f"Output rejected by guardrail: {output_result.reason}")
        return {
            "success": False,
            "error": output_result.reason,
            "response": "Generated response failed security or quality validation.",
            "stage": "output_guardrail",
            "guardrails": {
                "input": {"passed": True, "reason": None, "details": input_result.details},
                "output": {
                    "passed": False,
                    "reason": output_result.reason,
                    "grounding_score": output_result.score,
                    "details": output_result.details,
                },
            },
            "sources": [],
        }

    # Suppress citations/references if the model indicates no relevant information was found
    NO_INFO_INDICATORS = [
        "cannot find information to answer this question",
        "do not contain information to answer this question",
        "no information to answer this question",
        "not enough information in the provided transcripts",
        "based on the available video transcripts, i cannot find",
        "no matching video transcripts found",
    ]
    resp_text = output_result.sanitized_content or raw_response
    has_no_info = any(ind in resp_text.lower() for ind in NO_INFO_INDICATORS)
    final_sources = [] if has_no_info else retrieved_chunks

    return {
        "success": True,
        "response": resp_text,
        "stage": "completed",
        "guardrails": {
            "input": {
                "passed": True,
                "reason": None,
                "details": input_result.details,
            },
            "output": {
                "passed": True,
                "reason": None,
                "grounding_score": 0.0 if has_no_info else output_result.score,
                "details": "No relevant source segments found." if has_no_info else output_result.details,
            },
        },
        "sources": final_sources,
    }
