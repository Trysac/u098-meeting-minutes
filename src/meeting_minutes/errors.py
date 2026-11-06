"""Typed errors raised by the library."""

from __future__ import annotations

from typing import Literal

ErrorCode = Literal[
    "transcript_parse",
    "input_too_large",
    "format",
    "empty_transcript",
    "too_many_chunks",
]

MAX_QUOTE_CHARS = 200


def clip(text: str, limit: int = MAX_QUOTE_CHARS) -> str:
    """Return ``text`` cut to at most ``limit`` characters."""
    return text[:limit]


class MinutesError(Exception):
    """Base error of the library with a stable machine-readable ``code``.

    Attributes:
        code: One of the values of ``ErrorCode``.
        line: 1-based transcript line that caused a parse error, if any.
        raw: At most 200 characters of the offending input, if any.
    """

    def __init__(
        self,
        code: ErrorCode,
        message: str,
        *,
        line: int | None = None,
        raw: str | None = None,
    ) -> None:
        super().__init__(message)
        self.code: ErrorCode = code
        self.line = line
        self.raw = None if raw is None else clip(raw)
