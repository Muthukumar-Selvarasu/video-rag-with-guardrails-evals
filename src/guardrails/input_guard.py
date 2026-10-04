"""Input guardrails for intercepting and validating user queries."""

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class GuardrailResult:
    """Represents the outcome of a guardrail validation."""
    passed: bool
    reason: Optional[str] = None
    sanitized_content: Optional[str] = None
    score: Optional[float] = None
    details: Optional[Dict[str, Any]] = field(default_factory=dict)


class InputGuardrail:
    """Validates user prompts prior to agent execution."""

    # Common prompt injection triggers
    DEFAULT_INJECTION_PATTERNS = [
        r"(?i)ignore\s+(all\s+)?(previous|prior)\s+instructions",
        r"(?i)system\s+prompt\s+override",
        r"(?i)system\s+override",
        r"(?i)you\s+are\s+now\s+in\s+developer\s+mode",
        r"(?i)disregard\s+all\s+rules",
        r"(?i)forget\s+all\s+rules",
        r"(?i)reveal\s+(your\s+)?(secret|internal|system)\s+prompt",
        r"(?i)\b(dan|do\s+anything\s+now)\s+mode\b",
        r"(?i)\bbypass\s+safety\s+filters\b",
        r"(?i)\b(gemini_api_key|openai_api_key|api_key|admin\s+token)\b",
        r"(?i)\brm\s+-rf\b",
        r"(?i)\bformat\s+(the\s+hard\s+drive|c:)\b",
        r"(?i)\b(illegal\s+firearms|explosive\s+devices|manufacture\s+bombs)\b",
        r"(?i)<script\b",
        r"(?i)\b(phishing\s+email|phishing\s+attack)\b",
        r"(?i)\breveal\s+.*(passwords?|credit\s*cards?|database\s+connection)",
    ]

    # Off-topic domain patterns unrelated to course / video material
    DEFAULT_OFF_TOPIC_PATTERNS = [
        r"(?i)\b(recipe|bake\b|baking\b|cooking\b|ingredients\s+for)\b",
        r"(?i)\b(crypto\s+trading|buy\s+bitcoin|stock\s+prediction|forex)\b",
        r"(?i)\b(diagnose\s+my|medical\s+symptoms|prescription|dosage)\b",
        r"(?i)\b(write\s+an?\s+essay\s+on\s+world\s+war|write\s+a\s+poem\s+about\s+(flowers|cats))\b",
        r"(?i)\b(world\s+cup|fifa|olympics|super\s+bowl|nfl|nba)\b",
    ]

    def __init__(
        self,
        blocked_patterns: Optional[List[str]] = None,
        off_topic_patterns: Optional[List[str]] = None,
        course_keywords: Optional[List[str]] = None,
        enforce_course_relevance: bool = False,
        max_length: int = 4000,
    ):
        self.blocked_patterns = [
            re.compile(p) for p in (blocked_patterns or self.DEFAULT_INJECTION_PATTERNS)
        ]
        self.off_topic_patterns = [
            re.compile(p) for p in (off_topic_patterns or self.DEFAULT_OFF_TOPIC_PATTERNS)
        ]
        self.course_keywords = [kw.lower() for kw in (course_keywords or [])]
        self.enforce_course_relevance = enforce_course_relevance
        self.max_length = max_length

    def validate(self, query: str) -> GuardrailResult:
        """Validate input query against injection patterns, domain relevance, and length limits."""
        if not query or not query.strip():
            return GuardrailResult(
                passed=False,
                reason="Query cannot be empty.",
                details={"check": "empty_query"},
            )

        if len(query) > self.max_length:
            return GuardrailResult(
                passed=False,
                reason=f"Query exceeds maximum character limit of {self.max_length}.",
                details={"check": "max_length", "length": len(query)},
            )

        # 1. Prompt Injection Checks
        for pattern in self.blocked_patterns:
            if pattern.search(query):
                return GuardrailResult(
                    passed=False,
                    reason="Input triggered security guardrail (prompt injection detected).",
                    details={"check": "prompt_injection"},
                )

        # 2. Off-Topic Domain Filter
        for pattern in self.off_topic_patterns:
            if pattern.search(query):
                return GuardrailResult(
                    passed=False,
                    reason="Question is outside the scope of course video material.",
                    details={"check": "off_topic"},
                )

        # 3. Optional Strict Course Keyword / Topic Boundary Check
        if self.enforce_course_relevance and self.course_keywords:
            query_lower = query.lower()
            if not any(kw in query_lower for kw in self.course_keywords):
                return GuardrailResult(
                    passed=False,
                    reason="Question does not appear relevant to any indexed course topics.",
                    details={"check": "course_relevance"},
                )

        return GuardrailResult(
            passed=True,
            sanitized_content=query.strip(),
            details={"check": "passed", "injection_clean": True, "domain_relevant": True},
        )
