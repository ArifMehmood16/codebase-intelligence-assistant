"""Domain invariant violations. Not used for HTTP or infrastructure errors."""


class DomainError(Exception):
    """A domain rule was violated."""


class InvalidLineRangeError(DomainError):
    """A start/end line pair is not a valid 1-based inclusive range."""


class UnverifiedCitationError(DomainError):
    """A citation was not present in the retrieved set."""


class InvalidQuestionError(DomainError):
    """A question is missing or empty."""
