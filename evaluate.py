import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import time

from server import ChatError, ROOT, generate_answer, load_configuration
from gamedesk_tracing import flush_traces, initialize_tracing


def check_answer(test_case, actual):
    expected_rules = set(test_case["rule_ids"])
    actual_rules = set(actual["rule_ids"])
    checks = {
        "decision_matches": actual["decision"] == test_case["decision"],
        "required_references_present": expected_rules <= actual_rules,
    }
    return {
        "status": "pass" if all(checks.values()) else "mismatch",
        "checks": checks,
        "missing_references": sorted(expected_rules - actual_rules),
        "human_review_required": True,
        "review_notes": {
            "clarification_topics": test_case.get("must_ask_about", []),
            "claims_to_review": test_case.get("must_not_claim", []),
            "always_check": "Unsupported claims, appropriate clarification, and consistency between prose and decision.",
        },
    }


def run_evaluation(dataset, requirements, configuration, limit=None, interval=20, progress=None):
    selected = dataset["cases"][:limit] if limit else dataset["cases"]
    records = []
    stop_reason = None
    started = time.monotonic()
    for index, test_case in enumerate(selected):
        if stop_reason:
            records.append({"case_id": test_case["id"], "status": "not_run", "reason": stop_reason})
            continue
        if index and interval:
            time.sleep(interval)
        record = {
            "case_id": test_case["id"], "category": test_case["category"],
            "question": test_case["question"],
            "expected": {"decision": test_case["decision"], "rule_ids": test_case["rule_ids"]},
        }
        try:
            actual = generate_answer(test_case["question"], dataset["base_facts"], configuration, requirements)
            record.update(check_answer(test_case, actual))
            record["actual"] = actual
        except ChatError as error:
            record.update({"status": "error", "error": str(error), "http_status": error.status})
            if error.status in {429, 503}:
                stop_reason = "Stopped after a rate-limit or configuration error; no retries or paid fallback."
        records.append(record)
        if progress:
            progress(f"{record['case_id']}: {record['status']}")
    counts = {status: sum(record["status"] == status for record in records) for status in ("pass", "mismatch", "error", "not_run")}
    return {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "model": configuration["model"], "provider": "Groq",
        "dataset_version": dataset["version"], "requirements_version": requirements["version"],
        "expectations_status": "AI-drafted; human review pending",
        "criteria": "Exact decision and minimum required policy references; not a factual-correctness or hallucination score.",
        "settings": {"interval_seconds": interval, "case_limit": limit},
        "scenario_context": dataset["base_facts"],
        "duration_seconds": round(time.monotonic() - started, 2),
        "summary": {"selected": len(selected), **counts},
        "cases": records,
    }


def main():
    parser = argparse.ArgumentParser(description="Run real model checks against draft GameDesk expectations.")
    parser.add_argument("--limit", type=int, help="Run the first N development cases.")
    parser.add_argument("--interval", type=float, default=20, help="Seconds between calls; default 20 to reduce free-tier rate limits.")
    parser.add_argument("--output", type=Path, help="JSON report path; defaults to ignored results/private/.")
    args = parser.parse_args()
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be positive")
    if args.interval < 0:
        parser.error("--interval cannot be negative")
    configuration = load_configuration()
    if not configuration["key"]:
        parser.error("Set up your key first: python3 server.py --setup-key")
    initialize_tracing()
    dataset = json.loads((ROOT / "cases.json").read_text())
    requirements = json.loads((ROOT / "requirements.json").read_text())
    try:
        report = run_evaluation(dataset, requirements, configuration, args.limit, args.interval, lambda line: print(line, flush=True))
    finally:
        flush_traces()
    output = args.output or ROOT / "results" / "private" / (datetime.now(timezone.utc).strftime("run-%Y%m%dT%H%M%S%fZ") + ".json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(report["summary"]))
    print(f"Report: {output}")
    return 1 if report["summary"]["mismatch"] or report["summary"]["error"] or report["summary"]["not_run"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
