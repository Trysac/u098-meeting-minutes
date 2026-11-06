"""Render minutes as Markdown."""

from __future__ import annotations

from .models import ActionItem, Minutes


def _inline(text: str) -> str:
    return " ".join(text.split())


def _paragraph(text: str) -> str:
    flat = _inline(text)
    if flat.startswith(("#", ">", "-", "+", "*")):
        return "\\" + flat
    return flat


def _times(values: tuple[float, ...]) -> str:
    return ", ".join(repr(v) for v in values) or "none"


def _action(item: ActionItem) -> str:
    owner = _inline(item.owner) if item.owner else "unassigned"
    due = item.due.isoformat() if item.due else "none"
    note = " - owner unverified" if item.owner_unverified else ""
    task = _inline(item.task)
    evidence = _times(item.evidence_s)
    return f"[ ] {task} (owner: {owner}, due: {due}){note} (evidence: {evidence})"


def _section(title: str, entries: list[str]) -> list[str]:
    body = [f"- {entry}" for entry in entries] or ["- None"]
    return [f"## {title}", "", *body, ""]


def render_markdown(minutes: Minutes) -> str:
    """Render ``minutes`` as Markdown.

    Every value is collapsed to a single line so that model output cannot add headings or
    list structure of its own.
    """
    decisions = [f"{_inline(d.text)} (evidence: {_times(d.evidence_s)})" for d in minutes.decisions]
    lines = ["# Meeting minutes", "", "## Summary", "", _paragraph(minutes.summary), ""]
    lines += _section("Decisions", decisions)
    lines += _section("Action items", [_action(a) for a in minutes.action_items])
    lines += _section("Open questions", [_inline(q) for q in minutes.open_questions])
    lines += _section("Unverified", [_inline(u) for u in minutes.unverified])
    return "\n".join(lines).rstrip("\n") + "\n"
