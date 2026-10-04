# 📊 Video RAG Evaluation & Guardrail Verification Report

**Run Status**: **✅ PASSED**
- **Timestamp**: `2026-10-04T04:25:53Z`
- **Git Commit**: `541b6e4`
- **Evaluation Dataset**: `data/eval_golden_dataset.json` (55 samples)

---

## 🎯 Executive Metric Scorecard

| Metric | Target Gate | Current Score | Status | Description |
| :--- | :---: | :---: | :---: | :--- |
| **Context Precision** | **≥ 0.80** | **`0.9619`** | ✅ PASS | Mean reciprocal/average precision of ground-truth chunks in retrieval |
| **Faithfulness / Grounding** | **≥ 0.85** | **`0.9867`** | ✅ PASS | Proportion of generated claims grounded in transcript context |
| **Guardrail Pass Rate** | **≥ 0.90** | **`1.0000`** | ✅ PASS | Accuracy blocking adversarial queries and passing safe prompts |

---

## 📂 Category Breakdown

| Category | Samples | Avg Context Precision | Avg Faithfulness | Guardrail Pass Rate |
| :--- | :---: | :---: | :---: | :---: |
| `fact_retrieval` | 35 | `1.0000` | `0.9905` | `100.0%` |
| `multi_hop` | 10 | `0.8283` | `0.9600` | `100.0%` |
| `adversarial` | 10 | `N/A` | `1.0000` | `100.0%` |

---

## 🛡️ Guardrail Security Diagnostics
- **Prompt Injection & Jailbreak Defense**: 100% of synthetic attacks correctly intercepted at `input_guardrail`.
- **Credential Leak Prevention**: Zero API key or secret leakage detected in generated responses.
- **Transcript Grounding Enforcement**: Grounded refusal returned on out-of-domain knowledge queries.

---

## 🔍 Sample Evaluation Traces

| ID | Category | Query Snippet | Precision | Faithfulness | Verdict |
| :--- | :--- | :--- | :---: | :---: | :---: |
| `eval_fact_001` | fact_retrieval | Hamza Farug and Ash Faria introduction to the foundation of ... | 1.00 | 1.00 | ✅ Pass |
| `eval_fact_002` | fact_retrieval | 250 different individual companies and 10000 students across... | 1.00 | 1.00 | ✅ Pass |
| `eval_fact_003` | fact_retrieval | Anyone who has not installed or have not set up Claude with ... | 1.00 | 1.00 | ✅ Pass |
| `eval_fact_004` | fact_retrieval | GitHub repository called claw code start and first assignmen... | 1.00 | 1.00 | ✅ Pass |
| `eval_fact_005` | fact_retrieval | Models called sonnet or haiku with tools and execution loops... | 1.00 | 1.00 | ✅ Pass |
| `eval_fact_006` | fact_retrieval | Claude dot MD file skills file mcp server sub agent and hook... | 1.00 | 1.00 | ✅ Pass |
| `eval_fact_007` | fact_retrieval | Output which looks like AI safety and browser in Session 1... | 1.00 | 1.00 | ✅ Pass |
| `eval_fact_008` | fact_retrieval | Hey folks welcome to module two good morning good evening re... | 1.00 | 1.00 | ✅ Pass |
| `eval_fact_009` | fact_retrieval | Connect to brave mcp and fetch job description with resume i... | 1.00 | 1.00 | ✅ Pass |
| `eval_fact_010` | fact_retrieval | Agent has control and access to your entire system like loca... | 1.00 | 1.00 | ✅ Pass |
| `eval_fact_011` | fact_retrieval | Recap of skills we know that anything that has repetitive ta... | 1.00 | 1.00 | ✅ Pass |
| `eval_fact_012` | fact_retrieval | Breakdown of the costs associated of running and token break... | 1.00 | 1.00 | ✅ Pass |
| `eval_fact_013` | fact_retrieval | Research sub agent permissions to use brave MCP web search t... | 1.00 | 1.00 | ✅ Pass |
| `eval_fact_014` | fact_retrieval | One feedback we had as you all built out the assignment for ... | 1.00 | 1.00 | ✅ Pass |
| `eval_fact_015` | fact_retrieval | Hey folks good morning good evening yet another module and c... | 1.00 | 1.00 | ✅ Pass |

---
*Generated automatically by Video RAG Evaluation Suite (`tests.evals.report`)*
