"""Tests for the LLM port doubles."""

from __future__ import annotations

import pytest

from meeting_minutes import FakeLLM, RecordedLLM, RecordingExhaustedError

MESSAGES = [
    {"role": "system", "content": "rules"},
    {"role": "user", "content": "hello"},
]


def test_recorded_llm_replays_in_order_and_records_calls() -> None:
    llm = RecordedLLM(["one", "two"])
    assert llm.complete(MESSAGES, max_tokens=5) == "one"
    assert llm.complete(MESSAGES, max_tokens=7) == "two"
    assert llm.calls == [MESSAGES, MESSAGES]
    assert llm.calls[0] is not MESSAGES
    assert llm.max_tokens == [5, 7]


def test_recorded_llm_raises_when_exhausted_without_recording() -> None:
    llm = RecordedLLM(["only"])
    llm.complete(MESSAGES, max_tokens=1)
    for _ in range(3):
        with pytest.raises(RecordingExhaustedError):
            llm.complete(MESSAGES, max_tokens=1)
    assert len(llm.calls) == 1


def test_fake_llm_delegates_to_the_function() -> None:
    llm = FakeLLM(lambda messages: messages[-1]["content"].upper())
    assert llm.complete(MESSAGES, max_tokens=1) == "HELLO"
