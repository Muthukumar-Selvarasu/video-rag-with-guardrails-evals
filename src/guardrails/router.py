"""Interception router coordinating input validation, agent invocation, and output validation."""

import logging
import time
from typing import Any, Callable, Dict, List, Optional
from src.guardrails.input_guard import InputGuardrail, GuardrailResult
from src.guardrails.output_guard import OutputGuardrail
from src.telemetry.logger import get_telemetry_logger

logger = logging.getLogger(__name__)


class GuardrailRouter:
    """Orchestrates runtime guardrail checks around agent execution."""

    def __init__(
        self,
        input_guard: Optional[InputGuardrail] = None,
        output_guard: Optional[OutputGuardrail] = None,
    ):
        self.input_guard = input_guard or InputGuardrail()
        self.output_guard = output_guard or OutputGuardrail()
        self.telemetry = get_telemetry_logger()

    def process(
        self,
        query: str,
        agent_executor: Callable[[str], str],
        context: Optional[str] = None,
        session_id: Optional[str] = None,
        retrieval_chunk_ids: Optional[List[str]] = None,
        retrieval_latency_ms: float = 0.0,
    ) -> Dict[str, Any]:
        """Intercept input, invoke agent executor, and intercept output.

        Args:
            query: Raw user prompt.
            agent_executor: Callable that runs the agent and produces string response.
            context: Optional context retrieved during RAG execution.
            session_id: Optional session identifier for telemetry and tracking.
            retrieval_chunk_ids: Chunk IDs retrieved during RAG search.
            retrieval_latency_ms: Latency for retrieval in milliseconds.

        Returns:
            Dictionary with response text, guardrail pass flags, and metadata.
        """
        start_time = time.perf_counter()
        active_session_id = session_id or "default_session"
        active_chunk_ids = retrieval_chunk_ids or []

        # Step 1: Input Guardrail Check
        input_check = self.input_guard.validate(query)
        if not input_check.passed:
            total_duration_ms = (time.perf_counter() - start_time) * 1000.0
            logger.warning(f"Input rejected by guardrail: {input_check.reason}")
            self.telemetry.log_interaction(
                session_id=active_session_id,
                query=query,
                input_guard_passed=False,
                retrieval_chunk_ids=[],
                retrieval_latency_ms=0.0,
                llm_latency_ms=0.0,
                output_guard_passed=False,
                grounding_score=0.0,
                total_duration_ms=total_duration_ms,
                metadata={"stage": "input_guardrail", "reason": input_check.reason},
            )
            return {
                "success": False,
                "error": input_check.reason,
                "response": f"Request blocked: {input_check.reason}",
                "stage": "input_guardrail",
                "input_guardrail": {
                    "passed": False,
                    "reason": input_check.reason,
                    "details": input_check.details,
                },
                "output_guardrail": None,
            }

        sanitized_query = input_check.sanitized_content or query

        # Step 2: Agent Execution
        llm_start = time.perf_counter()
        try:
            raw_response = agent_executor(sanitized_query)
            llm_latency_ms = (time.perf_counter() - llm_start) * 1000.0
        except Exception as exc:
            llm_latency_ms = (time.perf_counter() - llm_start) * 1000.0
            total_duration_ms = (time.perf_counter() - start_time) * 1000.0
            logger.error(f"Agent execution failed: {exc}", exc_info=True)
            self.telemetry.log_interaction(
                session_id=active_session_id,
                query=query,
                input_guard_passed=True,
                retrieval_chunk_ids=active_chunk_ids,
                retrieval_latency_ms=retrieval_latency_ms,
                llm_latency_ms=llm_latency_ms,
                output_guard_passed=False,
                grounding_score=0.0,
                total_duration_ms=total_duration_ms,
                metadata={"stage": "agent_execution", "error": str(exc)},
            )
            return {
                "success": False,
                "error": str(exc),
                "response": "An error occurred while processing your request.",
                "stage": "agent_execution",
                "input_guardrail": {
                    "passed": True,
                    "reason": None,
                    "details": input_check.details,
                },
                "output_guardrail": None,
            }

        # Step 3: Output Guardrail Check
        output_check = self.output_guard.validate(raw_response, context=context)
        total_duration_ms = (time.perf_counter() - start_time) * 1000.0
        grounding_score = output_check.score if output_check.score is not None else 0.0

        if not output_check.passed:
            logger.warning(f"Output rejected by guardrail: {output_check.reason}")
            self.telemetry.log_interaction(
                session_id=active_session_id,
                query=query,
                input_guard_passed=True,
                retrieval_chunk_ids=active_chunk_ids,
                retrieval_latency_ms=retrieval_latency_ms,
                llm_latency_ms=llm_latency_ms,
                output_guard_passed=False,
                grounding_score=grounding_score,
                total_duration_ms=total_duration_ms,
                metadata={"stage": "output_guardrail", "reason": output_check.reason},
            )
            return {
                "success": False,
                "error": output_check.reason,
                "response": "Generated response failed security or quality validation.",
                "stage": "output_guardrail",
                "input_guardrail": {
                    "passed": True,
                    "reason": None,
                    "details": input_check.details,
                },
                "output_guardrail": {
                    "passed": False,
                    "reason": output_check.reason,
                    "grounding_score": output_check.score,
                    "details": output_check.details,
                },
            }

        self.telemetry.log_interaction(
            session_id=active_session_id,
            query=query,
            input_guard_passed=True,
            retrieval_chunk_ids=active_chunk_ids,
            retrieval_latency_ms=retrieval_latency_ms,
            llm_latency_ms=llm_latency_ms,
            output_guard_passed=True,
            grounding_score=grounding_score,
            total_duration_ms=total_duration_ms,
            metadata={"stage": "completed"},
        )

        return {
            "success": True,
            "response": output_check.sanitized_content,
            "stage": "completed",
            "input_guardrail": {
                "passed": True,
                "reason": None,
                "details": input_check.details,
            },
            "output_guardrail": {
                "passed": True,
                "reason": None,
                "grounding_score": output_check.score,
                "details": output_check.details,
            },
        }
