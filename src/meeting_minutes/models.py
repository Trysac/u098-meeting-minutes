"""Immutable data model of the library."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Utterance:
    """One transcript utterance.

    Attributes:
        speaker: Speaker name, or ``None`` when the format carries none.
        start_s: Start time in seconds (the 0-based line index for plain text).
        end_s: End time in seconds.
        text: Spoken text.
    """

    speaker: str | None
    start_s: float
    end_s: float
    text: str


@dataclass(frozen=True)
class Decision:
    """A decision taken in the meeting and the utterance times that support it."""

    text: str
    evidence_s: tuple[float, ...]


@dataclass(frozen=True)
class ActionItem:
    """A task with an optional verified owner and an optional due date."""

    task: str
    owner: str | None
    due: date | None
    evidence_s: tuple[float, ...]
    owner_unverified: bool = False


@dataclass(frozen=True)
class Minutes:
    """Validated meeting minutes.

    ``unverified`` holds the text of items whose evidence is not in the transcript.
    """

    summary: str
    decisions: tuple[Decision, ...] = ()
    action_items: tuple[ActionItem, ...] = ()
    open_questions: tuple[str, ...] = ()
    unverified: tuple[str, ...] = ()
