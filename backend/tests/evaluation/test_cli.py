"""CLI gate for the hermetic evaluation runner."""

from codebase_assistant.evaluation.__main__ import main


def test_evaluation_cli_exits_zero_for_baseline(capsys) -> None:
    assert main() == 0
    out = capsys.readouterr().out
    assert '"citation_validity_rate": 1.0' in out
    assert '"insufficient_evidence_correct_rate": 1.0' in out
    assert '"grounded_answer_file_hit_rate":' in out
