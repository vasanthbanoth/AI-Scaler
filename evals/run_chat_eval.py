#!/usr/bin/env python3
"""Golden-set chat eval — run after API + ingest are up."""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

API = os.getenv("API_BASE_URL", "http://localhost:8000")
GOLDEN = Path(__file__).parent / "golden_qa.json"
OUT = Path(__file__).parent / "runs" / "chat_eval.json"


def judge_answer(client: OpenAI, question: str, answer: str, must_contain: list, must_not_contain: list) -> dict:
    prompt = f"""You are an eval judge for a RAG chatbot.
Question: {question}
Answer: {answer}
Required phrases (any): {must_contain}
Forbidden phrases (none): {must_not_contain}

Return JSON only: {{"pass": bool, "grounded": bool, "hallucination": bool, "reason": str}}"""
    r = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": prompt}],
    )
    return json.loads(r.choices[0].message.content or "{}")


def main():
    cases = json.loads(GOLDEN.read_text())
    if not os.getenv("OPENAI_API_KEY"):
        print("OPENAI_API_KEY required for judge", file=sys.stderr)
        sys.exit(1)

    client = OpenAI()
    results = []
    latencies = []

    with httpx.Client(timeout=120) as http:
        for case in cases:
            t0 = time.perf_counter()
            r = http.post(f"{API}/chat", json={"message": case["question"]})
            latency = int((time.perf_counter() - t0) * 1000)
            latencies.append(latency)
            body = r.json()
            answer = body.get("reply", "")
            verdict = judge_answer(
                client,
                case["question"],
                answer,
                case.get("must_contain", []),
                case.get("must_not_contain", []),
            )
            results.append(
                {
                    "id": case["id"],
                    "question": case["question"],
                    "answer_preview": answer[:300],
                    "latency_ms": latency,
                    "sources": [s.get("source") for s in body.get("sources", [])[:3]],
                    **verdict,
                }
            )
            print(f"{case['id']}: pass={verdict.get('pass')} hallucination={verdict.get('hallucination')}")

    passed = sum(1 for x in results if x.get("pass"))
    hall = sum(1 for x in results if x.get("hallucination"))
    summary = {
        "n": len(results),
        "pass_rate": round(passed / len(results), 3),
        "hallucination_rate": round(hall / len(results), 3),
        "p50_latency_ms": sorted(latencies)[len(latencies) // 2],
        "p95_latency_ms": sorted(latencies)[int(len(latencies) * 0.95)],
        "results": results,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summary, indent=2))
    print(f"\nWrote {OUT}")
    print(f"pass_rate={summary['pass_rate']} hallucination_rate={summary['hallucination_rate']}")


if __name__ == "__main__":
    main()
