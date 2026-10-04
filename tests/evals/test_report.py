"""Unit tests for the evaluation report generator and regression gates."""

import json
from pathlib import Path
import pytest
from tests.evals.report import (
    compare_with_baseline,
    evaluate_faithfulness_claim,
    run_benchmark,
)


def test_evaluate_faithfulness_claim():
    """Verify claim grounding logic."""
    context = "Hamza Farooq and Ash Faria introduce foundations of Claude Code."
    gt = "Hamza Farooq introduces Claude Code."
    score = evaluate_faithfulness_claim(ground_truth=gt, context=context)
    assert score >= 0.8


def test_compare_with_baseline_no_regression(tmp_path):
    """Verify comparison passes when scores are on par or higher."""
    base_file = tmp_path / "base.json"
    base_file.write_text(json.dumps({
        "overall_metrics": {
            "context_precision": 0.90,
            "faithfulness": 0.95,
            "guardrail_pass_rate": 1.0,
        }
    }))

    current = {
        "context_precision": 0.92,
        "faithfulness": 0.96,
        "guardrail_pass_rate": 1.0,
    }
    passed, msgs = compare_with_baseline(current, base_file)
    assert passed is True
    assert len(msgs) == 0


def test_compare_with_baseline_regression_detected(tmp_path):
    """Verify regression is flagged when a score drops beyond tolerance."""
    base_file = tmp_path / "base.json"
    base_file.write_text(json.dumps({
        "overall_metrics": {
            "context_precision": 0.95,
            "faithfulness": 0.95,
            "guardrail_pass_rate": 1.0,
        }
    }))

    current = {
        "context_precision": 0.75,  # 0.20 drop > 0.05 tolerance
        "faithfulness": 0.95,
        "guardrail_pass_rate": 1.0,
    }
    passed, msgs = compare_with_baseline(current, base_file)
    assert passed is False
    assert any("context_precision" in m for m in msgs)


def test_run_benchmark_summary(tmp_path):
    """Verify execution against golden dataset produces expected summary structure."""
    dataset_path = Path("data/eval_golden_dataset.json")
    summary = run_benchmark(dataset_path=dataset_path, top_k=3)

    assert "overall_metrics" in summary
    assert summary["overall_metrics"]["context_precision"] >= 0.80
    assert summary["overall_metrics"]["faithfulness"] >= 0.85
    assert summary["overall_metrics"]["guardrail_pass_rate"] >= 0.90
    assert summary["total_samples"] == 55
