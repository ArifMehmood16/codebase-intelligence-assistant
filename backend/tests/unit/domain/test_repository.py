import pytest

from codebase_assistant.domain import DomainError, Repository, SourceFile


def test_repository_requires_id() -> None:
    with pytest.raises(DomainError):
        Repository(repository_id="  ")


def test_source_file_requires_path() -> None:
    with pytest.raises(DomainError):
        SourceFile(path="", content="print(1)")
