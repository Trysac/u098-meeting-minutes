"""Tests for the package surface."""

from __future__ import annotations

import logging

import meeting_minutes


def test_all_names_exist() -> None:
    for name in meeting_minutes.__all__:
        assert hasattr(meeting_minutes, name)


def test_version() -> None:
    assert meeting_minutes.__version__ == "0.1.0"


def test_logger_only_has_a_null_handler() -> None:
    handlers = logging.getLogger("meeting_minutes").handlers
    assert any(isinstance(h, logging.NullHandler) for h in handlers)
