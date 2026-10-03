"""Output guardrails for checking agent responses for hallucinations and policy violations."""

import re
from typing import Any, Dict, List, Optional
from src.guardrails.input_guard import GuardrailResult


class OutputGuardrail:
    """Validates and filters model responses before returning to the user."""

    # Sensitive token leaks
    DEFAULT_LEAK_PATTERNS = [
        r"(?i)api[_-]?key\s*[:=]\s*['\"]?[a-zA-Z0-9_\-]{16,}['\"]?",
        r"(?i)bearer\s+[a-zA-Z0-9_\-\.]{20,}",
    ]

    # Legitimate context absence refusals
    GROUNDED_REFUSAL_PHRASES = [
        "cannot find information",
        "not mentioned in the video",
        "not found in the transcript",
        "available video transcripts do not",
        "transcripts do not contain",
    ]

    def __init__(
        self,
        leak_patterns: Optional[List[str]] = None,
        min_grounding_score: float = 0.0,
    ):
        self.leak_patterns = [
            re.compile(p) for p in (leak_patterns or self.DEFAULT_LEAK_PATTERNS)
        ]
        self.min_grounding_score = min_grounding_score

    def compute_grounding_score(self, response: str, context: str) -> float:
        """Compute keyword grounding ratio between response statements and retrieved context."""
        stop_words = {
            "the", "a", "an", "in", "on", "at", "to", "for", "of", "and", "is",
            "are", "was", "were", "it", "this", "that", "with", "as", "by", "from",
            "we", "you", "they", "i", "or", "be", "so", "can", "if", "not", "but",
        }
        resp_tokens = {
            w for w in re.findall(r"\b[a-zA-Z0-9_-]{3,}\b", response.lower())
            if w not in stop_words
        }
        ctx_tokens = {
            w for w in re.findall(r"\b[a-zA-Z0-9_-]{3,}\b", context.lower())
            if w not in stop_words
        }
        if not resp_tokens:
            return 1.0
        overlap = resp_tokens.intersection(ctx_tokens)
        return len(overlap) / len(resp_tokens)

    def _compute_grounding_ratio(self, response: str, context: str) -> float:
        """Alias for backward compatibility."""
        return self.compute_grounding_score(response, context)

    def validate(self, response: str, context: Optional[str] = None) -> GuardrailResult:
        """Validate agent output against leaks and real-time grounding safety criteria.

        Args:
            response: Generated answer text.
            context: Optional retrieved context chunks to verify grounding.

        Returns:
            GuardrailResult with pass/fail status, grounding score, and sanitized response.
        """
        if not response or not response.strip():
            return GuardrailResult(
                passed=False,
                reason="Agent response was empty.",
                details={"check": "empty_response"},
            )

        # 1. Check for credential or token leakage
        for pattern in self.leak_patterns:
            if pattern.search(response):
                return GuardrailResult(
                    passed=False,
                    reason="Output contained potential secret or API key leakage.",
                    details={"check": "credential_leak"},
                )

        grounding_score: Optional[float] = None
        # 2. Real-time pre-response evaluation: Grounding / Hallucination verification
        if context:
            grounding_score = round(self.compute_grounding_score(response, context), 4)
            resp_lower = response.lower()
            is_refusal = any(phrase in resp_lower for phrase in self.GROUNDED_REFUSAL_PHRASES)

            if self.min_grounding_score > 0.0 and not is_refusal:
                if grounding_score < self.min_grounding_score:
                    return GuardrailResult(
                        passed=False,
                        reason=(
                            f"Output failed grounding validation against retrieved video "
                            f"transcript context (grounding score: {grounding_score:.2f} < {self.min_grounding_score:.2f})."
                        ),
                        score=grounding_score,
                        details={
                            "check": "grounding_failed",
                            "grounding_score": grounding_score,
                            "min_grounding_score": self.min_grounding_score,
                        },
                    )

        return GuardrailResult(
            passed=True,
            sanitized_content=response.strip(),
            score=grounding_score,
            details={
                "check": "passed",
                "leak_clean": True,
                "grounding_score": grounding_score,
            },
        )
