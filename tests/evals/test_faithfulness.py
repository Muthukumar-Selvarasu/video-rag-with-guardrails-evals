"""Evaluation tests for Faithfulness metric in RAG pipelines."""

import os

try:
    import pytest
except ImportError:
    class MockPytest:
        @staticmethod
        def fixture(func):
            return func

        class mark:
            @staticmethod
            def skipif(*args, **kwargs):
                def decorator(func):
                    return func
                return decorator

    pytest = MockPytest()  # type: ignore


def calculate_faithfulness_heuristic(statement: str, context: str) -> float:
    """Heuristic calculation of statement grounding against context chunks.

    Used for deterministic CI evaluations when external LLM evaluation APIs are offline.
    """
    statement_words = set(statement.lower().split())
    context_words = set(context.lower().split())

    if not statement_words:
        return 0.0

    overlap = statement_words.intersection(context_words)
    return len(overlap) / len(statement_words)


@pytest.fixture
def sample_video_rag_data():
    return {
        "question": "What is the primary benefit of speculative decoding discussed in the lecture?",
        "context": (
            "At 04:12, Professor Smith explains speculative decoding. "
            "Speculative decoding accelerates inference latency by utilizing a smaller draft model "
            "to generate candidate tokens, which are verified in parallel by the target model."
        ),
        "grounded_answer": "Speculative decoding accelerates inference latency by using a draft model to generate tokens verified by the target model.",
        "hallucinated_answer": "Speculative decoding reduces model memory footprint by compressing weights into 4-bit integers.",
    }


def test_faithfulness_grounded_response(sample_video_rag_data):
    """Verify that a faithful answer scores high grounding against retrieved transcript context."""
    score = calculate_faithfulness_heuristic(
        statement=sample_video_rag_data["grounded_answer"],
        context=sample_video_rag_data["context"],
    )
    # Grounded answer should have significant word/concept overlap with context
    assert score >= 0.5, f"Expected faithfulness >= 0.5, got {score}"


def test_faithfulness_hallucinated_response(sample_video_rag_data):
    """Verify that an ungrounded/hallucinated answer scores low grounding against context."""
    score = calculate_faithfulness_heuristic(
        statement=sample_video_rag_data["hallucinated_answer"],
        context=sample_video_rag_data["context"],
    )
    # Hallucinated answer introduces unrelated concepts (memory footprint, 4-bit)
    assert score < 0.5, f"Expected hallucination score < 0.5, got {score}"


@pytest.mark.skipif(
    not os.getenv("GEMINI_API_KEY"),
    reason="GEMINI_API_KEY not configured for live LLM evaluation run",
)
def test_faithfulness_ragas_live(sample_video_rag_data):
    """Live RAGAS faithfulness metric evaluation test (executed only when GEMINI_API_KEY is present)."""
    try:
        from ragas import evaluate
        from ragas.metrics import faithfulness
        from datasets import Dataset

        data = {
            "question": [sample_video_rag_data["question"]],
            "contexts": [[sample_video_rag_data["context"]]],
            "answer": [sample_video_rag_data["grounded_answer"]],
        }
        dataset = Dataset.from_dict(data)
        result = evaluate(dataset, metrics=[faithfulness])
        assert result["faithfulness"] >= 0.7
    except ImportError:
        pytest.skip("ragas or datasets library not installed in current environment")
