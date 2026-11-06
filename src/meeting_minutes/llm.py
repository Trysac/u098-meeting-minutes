"""LLM port and deterministic test doubles."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Literal, Protocol, TypedDict


class Message(TypedDict):
    """One chat message."""

    role: Literal["system", "user", "assistant"]
    content: str


class LLMPort(Protocol):
    """Port that every language-model adapter implements."""

    def complete(self, messages: Sequence[Message], *, max_tokens: int) -> str:
        """Return the model reply for ``messages``; adapter exceptions propagate unchanged."""
        ...


class RecordingExhaustedError(RuntimeError):
    """Raised by ``RecordedLLM`` when every recorded reply has been used."""


class RecordedLLM:
    """Replays fixed replies in order and records every call (test double).

    The number of recorded calls never exceeds the number of replies.
    """

    def __init__(self, replies: Sequence[str]) -> None:
        self._replies = tuple(replies)
        self.calls: list[list[Message]] = []
        self.max_tokens: list[int] = []

    def complete(self, messages: Sequence[Message], *, max_tokens: int) -> str:
        """Return the next recorded reply or raise ``RecordingExhaustedError``."""
        if len(self.calls) >= len(self._replies):
            raise RecordingExhaustedError("no recorded reply left")
        self.calls.append([{"role": m["role"], "content": m["content"]} for m in messages])
        self.max_tokens.append(max_tokens)
        return self._replies[len(self.calls) - 1]


class FakeLLM:
    """Delegates every call to a function (test double)."""

    def __init__(self, fn: Callable[[Sequence[Message]], str]) -> None:
        self._fn = fn

    def complete(self, messages: Sequence[Message], *, max_tokens: int) -> str:
        """Return ``fn(messages)``."""
        return self._fn(messages)
