"""Resolve relative due-date phrases."""

from __future__ import annotations

import re
from datetime import date, timedelta

from .errors import MinutesError

MAX_DATE_TEXT_CHARS = 200

_WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}
_WEEKDAY_PHRASE = re.compile(r"(this|next) ([a-z]+)")
_OFFSET_PHRASE = re.compile(r"in ([0-9]{1,4}) (day|days|week|weeks)")
_ISO_DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")


def resolve_relative_date(text: str, today: date) -> date | None:
    """Resolve a due-date phrase relative to ``today``.

    Supported (case-insensitive): ``today``, ``tomorrow``, ``this WEEKDAY`` (next occurrence
    after today), ``next WEEKDAY`` (the ``this`` date plus 7 days when it falls in the current
    Monday-based week, otherwise the ``this`` date), ``in N days``, ``in N weeks`` and ISO
    ``YYYY-MM-DD``. Returns ``None`` for anything else or when the result is out of range.

    Raises:
        MinutesError: ``input_too_large`` when ``text`` has more than 200 characters.
    """
    if len(text) > MAX_DATE_TEXT_CHARS:
        raise MinutesError(
            "input_too_large",
            f"date phrase exceeds {MAX_DATE_TEXT_CHARS} characters",
        )
    phrase = " ".join(text.lower().split())
    try:
        return _resolve(phrase, today)
    except (OverflowError, ValueError):
        return None


def _resolve(phrase: str, today: date) -> date | None:
    if phrase == "today":
        return today
    if phrase == "tomorrow":
        return today + timedelta(days=1)
    if _ISO_DATE.fullmatch(phrase):
        return date.fromisoformat(phrase)
    weekday = _WEEKDAY_PHRASE.fullmatch(phrase)
    if weekday and weekday.group(2) in _WEEKDAYS:
        return _weekday_date(weekday.group(1), _WEEKDAYS[weekday.group(2)], today)
    offset = _OFFSET_PHRASE.fullmatch(phrase)
    if offset:
        unit = 7 if offset.group(2).startswith("week") else 1
        return today + timedelta(days=int(offset.group(1)) * unit)
    return None


def _weekday_date(which: str, target: int, today: date) -> date:
    result = today + timedelta(days=(target - today.weekday()) % 7 or 7)
    if which == "next":
        monday = today - timedelta(days=today.weekday())
        if result < monday + timedelta(days=7):
            result += timedelta(days=7)
    return result
