"""Hermetic retrieval evaluation runner (PLAN 9.3)."""

from codebase_assistant.evaluation.runner import run_evaluation


def test_evaluation_runner_reports_observed_metrics() -> None:
    report = run_evaluation(retrieval_k=5)
    assert report.embedding_provider == "lexical"
    assert report.completion_provider == "extractive"
    assert report.retrieval_k == 5
    assert len(report.cases) >= 6
    assert report.citation_validity_rate == 1.0
    assert report.insufficient_evidence_correct_rate == 1.0
    assert report.grounded_source_hit_rate >= 0.75
    assert report.grounded_answer_file_hit_rate >= 0.8
    by_id = {case.case_id: case for case in report.cases}
    locate = by_id["list-items-location"]
    assert locate.answer_file_hit is True
    assert "src/api/handlers.py" in locate.cited_files
    endpoints = by_id["api-endpoints"]
    assert endpoints.outcome_ok is True
    assert "src/api/handlers.py" in endpoints.cited_files
    for case in report.cases:
        assert case.latency_ms >= 0.0
        assert case.citation_valid is True
