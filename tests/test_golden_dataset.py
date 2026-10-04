"""Tests verifying the schema, integrity, and safety of data/eval_golden_dataset.json."""

import json
import re
from pathlib import Path
import pytest

DATASET_PATH = Path("data/eval_golden_dataset.json")
INDEX_PATH = Path("data/preindexed_embeddings.json")

REQUIRED_KEYS = {
    "id",
    "query",
    "ground_truth",
    "relevant_chunk_ids",
    "expected_guardrail_pass",
    "session_id",
}


@pytest.fixture(scope="module")
def dataset_items():
    assert DATASET_PATH.exists(), f"Golden dataset missing at {DATASET_PATH}"
    with open(DATASET_PATH, encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, list), "Golden dataset must be a JSON array"
    return data


@pytest.fixture(scope="module")
def valid_chunk_ids():
    assert INDEX_PATH.exists(), f"Preindexed embeddings missing at {INDEX_PATH}"
    with open(INDEX_PATH, encoding="utf-8") as f:
        idx_data = json.load(f)
    return {c["id"] for c in idx_data.get("chunks", [])}


def test_dataset_size_and_categories(dataset_items):
    """Verify minimum 50 items and required composition."""
    assert len(dataset_items) >= 50, f"Expected >= 50 items, found {len(dataset_items)}"

    fact_count = sum(1 for item in dataset_items if item.get("category") == "fact_retrieval")
    multi_count = sum(1 for item in dataset_items if item.get("category") == "multi_hop")
    adv_count = sum(1 for item in dataset_items if item.get("category") == "adversarial")

    assert fact_count >= 35, f"Expected >= 35 fact-retrieval samples, got {fact_count}"
    assert multi_count >= 10, f"Expected >= 10 multi-hop samples, got {multi_count}"
    assert adv_count >= 10, f"Expected >= 10 adversarial/out-of-scope samples, got {adv_count}"


def test_schema_integrity(dataset_items):
    """Verify all samples conform to the required schema."""
    seen_ids = set()
    for idx, sample in enumerate(dataset_items):
        missing_keys = REQUIRED_KEYS - set(sample.keys())
        assert not missing_keys, f"Sample #{idx} (id={sample.get('id')}) missing keys: {missing_keys}"

        sample_id = sample["id"]
        assert isinstance(sample_id, str) and sample_id.strip(), f"Invalid ID in sample #{idx}"
        assert sample_id not in seen_ids, f"Duplicate ID '{sample_id}' found"
        seen_ids.add(sample_id)

        assert isinstance(sample["query"], str) and len(sample["query"].strip()) > 5
        assert isinstance(sample["ground_truth"], str) and len(sample["ground_truth"].strip()) > 5
        assert isinstance(sample["relevant_chunk_ids"], list)
        assert isinstance(sample["expected_guardrail_pass"], bool)
        assert sample["session_id"] is None or isinstance(sample["session_id"], str)


def test_chunk_ids_grounding(dataset_items, valid_chunk_ids):
    """Verify all non-adversarial chunk IDs exist in preindexed_embeddings.json."""
    for sample in dataset_items:
        chunk_ids = sample.get("relevant_chunk_ids", [])
        if sample.get("category") == "adversarial" and not chunk_ids:
            continue

        assert len(chunk_ids) > 0, f"Expected relevant_chunk_ids for {sample['id']}"
        for cid in chunk_ids:
            assert cid in valid_chunk_ids, f"Chunk ID '{cid}' in {sample['id']} does not exist in vector index"


def test_no_credentials_or_pii_leaks(dataset_items):
    """Verify no API keys, secrets, or sensitive credentials leaked in dataset."""
    secret_patterns = [
        re.compile(r"AIza[0-9A-Za-z-_]{35}"),
        re.compile(r"sk-[a-zA-Z0-9]{20,}"),
        re.compile(r"ghp_[a-zA-Z0-9]{36}"),
        re.compile(r"password\s*=\s*['\"][^'\"]+['\"]", re.IGNORECASE),
        re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"),
    ]

    for sample in dataset_items:
        text_content = f"{sample['query']} {sample['ground_truth']}"
        for pattern in secret_patterns:
            matches = pattern.findall(text_content)
            real_leaks = [m for m in matches if "example.com" not in m]
            assert not real_leaks, f"Sensitive pattern leak detected in {sample['id']}: {real_leaks}"
