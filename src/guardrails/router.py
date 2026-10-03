"""Interception router coordinating input validation, agent invocation, and output validation."""

import logging
from typing import Any, Callable, Dict, Optional
from src.guardrails.input_guard import InputGuardrail, GuardrailResult
from src.guardrails.output_guard import OutputGuardrail

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

    def process(
        self,
        query: str,
        agent_executor: Callable[[str], str],
        context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Intercept input, invoke agent executor, and intercept output.

        Args:
            query: Raw user prompt.
            agent_executor: Callable that runs the agent and produces string response.
            context: Optional context retrieved during RAG execution.

        Returns:
            Dictionary with response text, guardrail pass flags, and metadata.
        """
        # Step 1: Input Guardrail Check
        input_check = self.input_guard.validate(query)
        if not input_check.passed:
            logger.warning(f"Input rejected by guardrail: {input_check.reason}")
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
        try:
            raw_response = agent_executor(sanitized_query)
        except Exception as exc:
            logger.error(f"Agent execution failed: {exc}", exc_info=True)
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
        if not output_check.passed:
            logger.warning(f"Output rejected by guardrail: {output_check.reason}")
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
