"""Tests for resolve_relative_date."""

from __future__ import annotations

from datetime import date

import pytest

from meeting_minutes import MinutesError, resolve_relative_date

TODAY = date(2026, 11, 5)


@pytest.mark.parametrize(
    ("phrase", "expected"),
    [
        ("next Friday", date(2026, 11, 13)),
        ("this Friday", date(2026, 11, 6)),
        ("next Monday", date(2026, 11, 9)),
        ("in 2 weeks", date(2026, 11, 19)),
        ("soon", None),
        ("today", date(2026, 11, 5)),
        ("Tomorrow", date(2026, 11, 6)),
        ("this Monday", date(2026, 11, 9)),
        ("this Thursday", date(2026, 11, 12)),
        ("next Thursday", date(2026, 11, 12)),
        ("this Sunday", date(2026, 11, 8)),
        ("next Sunday", date(2026, 11, 15)),
        ("  NEXT   friday ", date(2026, 11, 13)),
        ("in 1 day", date(2026, 11, 6)),
        ("in 3 DAYS", date(2026, 11, 8)),
        ("in 0 days", date(2026, 11, 5)),
        ("2026-12-31", date(2026, 12, 31)),
        ("2026-02-30", None),
        ("0000-01-01", None),
        ("this funday", None),
        ("in two weeks", None),
        ("in 99999 days", None),
        ("in 2 weeks please", None),
        ("", None),
        ("next", None),
        ("2026-1-5", None),
    ],
)
def test_phrases(phrase: str, expected: date | None) -> None:
    assert resolve_relative_date(phrase, TODAY) == expected


def test_out_of_range_results_are_none() -> None:
    assert resolve_relative_date("tomorrow", date.max) is None
    assert resolve_relative_date("this Friday", date.max) is None
    assert resolve_relative_date("next Monday", date.min) is not None
    assert resolve_relative_date("in 9999 weeks", date(9900, 1, 1)) is None


def test_phrase_length_limit() -> None:
    assert resolve_relative_date("x" * 200, TODAY) is None
    with pytest.raises(MinutesError) as info:
        resolve_relative_date("x" * 201, TODAY)
    assert info.value.code == "input_too_large"
