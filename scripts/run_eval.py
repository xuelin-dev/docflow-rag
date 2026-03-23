"""Trigger an evaluation run via the DocFlow RAG API.

Usage:
    python scripts/run_eval.py                          # default eval set
    python scripts/run_eval.py --eval-set qa_pairs.json
    python scripts/run_eval.py --base-url http://prod:8000 --namespace default
"""

import argparse
import json
import sys
from pathlib import Path

import httpx

DEFAULT_BASE_URL = "http://localhost:8000"
DEFAULT_EVAL_SET = "eval/qa_pairs.json"


def load_eval_set(path: str) -> list[dict]:
    """Load evaluation question-answer pairs from a JSON file."""
    eval_path = Path(path)
    if not eval_path.exists():
        print(f"Error: Evaluation set not found at {eval_path}")
        sys.exit(1)

    with open(eval_path) as f:
        data = json.load(f)

    if not isinstance(data, list):
        print("Error: Evaluation set must be a JSON array of objects")
        sys.exit(1)

    return data


def run_evaluation(
    base_url: str,
    eval_set: list[dict],
    namespace: str = "default",
) -> dict:
    """Run evaluation queries and collect results."""
    results = []
    total = len(eval_set)

    for i, item in enumerate(eval_set, 1):
        question = item["question"]
        expected = item.get("expected_answer", "")
        expected_sources = item.get("expected_sources", [])

        print(f"[{i}/{total}] Evaluating: {question[:80]}...")

        try:
            response = httpx.post(
                f"{base_url}/api/v1/query",
                json={
                    "query": question,
                    "namespace": namespace,
                    "top_k": 5,
                    "rerank": True,
                },
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()

            result = {
                "question": question,
                "expected_answer": expected,
                "actual_answer": data.get("answer", ""),
                "sources": [s.get("source", "") for s in data.get("sources", [])],
                "expected_sources": expected_sources,
                "latency_ms": response.elapsed.total_seconds() * 1000,
                "status": "success",
            }
        except httpx.HTTPError as e:
            result = {
                "question": question,
                "status": "error",
                "error": str(e),
            }

        results.append(result)

    # Compute summary metrics
    successful = [r for r in results if r["status"] == "success"]
    avg_latency = (
        sum(r["latency_ms"] for r in successful) / len(successful)
        if successful
        else 0
    )

    summary = {
        "total_queries": total,
        "successful": len(successful),
        "failed": total - len(successful),
        "avg_latency_ms": round(avg_latency, 2),
        "results": results,
    }

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run DocFlow RAG evaluation")
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"API base URL (default: {DEFAULT_BASE_URL})",
    )
    parser.add_argument(
        "--eval-set",
        default=DEFAULT_EVAL_SET,
        help=f"Path to evaluation JSON file (default: {DEFAULT_EVAL_SET})",
    )
    parser.add_argument(
        "--namespace",
        default="default",
        help="Namespace to query (default: default)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output file for results JSON (default: stdout)",
    )
    args = parser.parse_args()

    eval_set = load_eval_set(args.eval_set)
    print(f"Loaded {len(eval_set)} evaluation queries from {args.eval_set}")
    print(f"Target: {args.base_url} (namespace: {args.namespace})")
    print("-" * 60)

    summary = run_evaluation(args.base_url, eval_set, args.namespace)

    print("-" * 60)
    print(f"Results: {summary['successful']}/{summary['total_queries']} successful")
    print(f"Average latency: {summary['avg_latency_ms']:.1f} ms")

    output_json = json.dumps(summary, indent=2, ensure_ascii=False)

    if args.output:
        Path(args.output).write_text(output_json)
        print(f"Results saved to {args.output}")
    else:
        print("\n" + output_json)


if __name__ == "__main__":
    main()
