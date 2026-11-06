"""Tests for render_markdown."""

from __future__ import annotations

from datetime import date

from meeting_minutes import ActionItem, Decision, Minutes, render_markdown


def test_render_full_minutes() -> None:
    minutes = Minutes(
        summary="We met.\nShip it.",
        decisions=(Decision("Ship on Friday", (2.5,)),),
        action_items=(
            ActionItem("Write notes", "Alice", date(2026, 11, 13), (1.0,), False),
            ActionItem("Call vendor", None, None, (3.0, 4.0), True),
        ),
        open_questions=("Who owns QA?",),
        unverified=("Invented task",),
    )
    expected = "\n".join(
        [
            "# Meeting minutes",
            "",
            "## Summary",
            "",
            "We met. Ship it.",
            "",
            "## Decisions",
            "",
            "- Ship on Friday (evidence: 2.5)",
            "",
            "## Action items",
            "",
            "- [ ] Write notes (owner: Alice, due: 2026-11-13) (evidence: 1.0)",
            "- [ ] Call vendor (owner: unassigned, due: none) - owner unverified"
            " (evidence: 3.0, 4.0)",
            "",
            "## Open questions",
            "",
            "- Who owns QA?",
            "",
            "## Unverified",
            "",
            "- Invented task",
            "",
        ]
    )
    assert render_markdown(minutes) == expected


def test_render_empty_sections() -> None:
    text = render_markdown(Minutes(summary="Short."))
    assert text.count("- None") == 4
    assert text.endswith("- None\n")


def test_render_cannot_be_hijacked_by_newlines() -> None:
    minutes = Minutes(
        summary="# Hacked\n## Heading",
        decisions=(Decision("a\n## Fake", ()),),
        open_questions=("q\n\n# Other",),
    )
    text = render_markdown(minutes)
    assert "\\# Hacked ## Heading" in text
    assert "\n## Fake" not in text
    assert "\n# Other" not in text
    assert "(evidence: none)" in text
