"""CLI entry for the hermetic retrieval evaluation runner."""

from __future__ import annotations

import json
import sys

from codebase_assistant.evaluation.runner import run_evaluation


def main(argv: list[str] | None = None) -> int:
    del argv  # reserved for future flags
    report = run_evaluation()
    payload = {
        "embedding_provider": report.embedding_provider,
        "completion_provider": report.completion_provider,
        "retrieval_k": report.retrieval_k,
        "dataset_path": report.dataset_path,
        "fixture_repository": report.fixture_repository,
        "outcome_pass_rate": report.outcome_pass_rate,
        "grounded_source_hit_rate": report.grounded_source_hit_rate,
        "grounded_answer_file_hit_rate": report.grounded_answer_file_hit_rate,
        "citation_validity_rate": report.citation_validity_rate,
        "insufficient_evidence_correct_rate": report.insufficient_evidence_correct_rate,
        "cases": [
            {
                "case_id": case.case_id,
                "expect_kind": case.expect_kind,
                "latency_ms": round(case.latency_ms, 3),
                "insufficient_evidence": case.insufficient_evidence,
                "retrieved_files": list(case.retrieved_files),
                "cited_files": list(case.cited_files),
                "source_hit_at_k": case.source_hit_at_k,
                "answer_file_hit": case.answer_file_hit,
                "citation_valid": case.citation_valid,
                "outcome_ok": case.outcome_ok,
            }
            for case in report.cases
        ],
    }
    json.dump(payload, sys.stdout, indent=2)
    sys.stdout.write("\n")
    # Gate on citation validity, IE correctness, and grounded cited-file hit.
    ok = (
        report.citation_validity_rate == 1.0
        and report.insufficient_evidence_correct_rate == 1.0
        and report.grounded_source_hit_rate >= 0.75
        and report.grounded_answer_file_hit_rate >= 0.8
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
