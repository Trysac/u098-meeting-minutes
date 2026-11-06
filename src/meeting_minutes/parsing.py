"""Transcript parsers for plain text, SubRip and WebVTT."""

from __future__ import annotations

import html
import re
from typing import Literal

from .errors import MinutesError, clip
from .models import Utterance

DEFAULT_MAX_INPUT_CHARS = 2_000_000
MAX_SPEAKER_CHARS = 40
_QUOTE_CHARS = 100

_SRT_STAMP = r"(\d{2,4}):(\d{2}):(\d{2}),(\d{3})"
_VTT_STAMP = r"(?:(\d{2,4}):)?(\d{2}):(\d{2})\.(\d{3})"
_SRT_INDEX = re.compile(r"[0-9]+")
_SRT_TIME = re.compile(f"{_SRT_STAMP} --> {_SRT_STAMP}", re.ASCII)
_VTT_TIME = re.compile(rf"{_VTT_STAMP}[ \t]+-->[ \t]+{_VTT_STAMP}(?:[ \t]+.*)?", re.ASCII)
_VOICE = re.compile(r"<v(?:\.[^\s>]{0,50}){0,10}[ \t]+([^<>]{1,100})>")
_TAG = re.compile(r"<[^<>]{0,200}>")


def parse_transcript(
    text: str,
    fmt: Literal["plain", "srt", "vtt"],
    *,
    max_input_chars: int = DEFAULT_MAX_INPUT_CHARS,
) -> list[Utterance]:
    """Parse a transcript into utterances.

    Formats: ``plain`` (``Speaker: text`` lines; times are the 0-based line index), ``srt``
    (SubRip cues) and ``vtt`` (WebVTT with optional hours, cue ids, settings, NOTE/STYLE blocks
    and ``<v Speaker>`` tags). A BOM and CRLF line endings are accepted.

    Raises:
        MinutesError: ``input_too_large`` above ``max_input_chars`` characters,
            ``transcript_parse`` (with ``line``) for malformed input and
            ``empty_transcript`` when no utterance is found.
    """
    if len(text) > max_input_chars:
        raise MinutesError(
            "input_too_large",
            f"transcript exceeds {max_input_chars} characters",
        )
    lines = _split_lines(text)
    if fmt == "plain":
        utterances = _parse_plain(lines)
    elif fmt == "srt":
        utterances = _parse_srt(lines)
    elif fmt == "vtt":
        utterances = _parse_vtt(lines)
    else:
        raise MinutesError("transcript_parse", f"unsupported format {clip(str(fmt), 40)!r}")
    if not utterances:
        raise MinutesError("empty_transcript", "the transcript has no utterances")
    return utterances


def _split_lines(text: str) -> list[str]:
    cleaned = text.removeprefix("\ufeff")
    return cleaned.replace("\r\n", "\n").replace("\r", "\n").split("\n")


def _fail(message: str, line: int, quoted: str = "") -> MinutesError:
    detail = f"{message}: {clip(quoted, _QUOTE_CHARS)!r}" if quoted else message
    return MinutesError("transcript_parse", f"line {line}: {detail}", line=line)


def _parse_plain(lines: list[str]) -> list[Utterance]:
    utterances: list[Utterance] = []
    for index, raw in enumerate(lines):
        line = raw.strip()
        if not line:
            continue
        speaker: str | None = None
        body = line
        colon = line.find(":")
        if 1 <= colon <= MAX_SPEAKER_CHARS and line.startswith(": ", colon):
            candidate = line[:colon].strip()
            rest = line[colon + 2 :].strip()
            if candidate and rest:
                speaker = candidate
                body = rest
        utterances.append(Utterance(speaker, float(index), float(index), body))
    return utterances


def _seconds(hours: str | None, minutes: str, seconds: str, millis: str) -> float:
    return int(hours or 0) * 3600 + int(minutes) * 60 + int(seconds) + int(millis) / 1000


def _timing(match: re.Match[str], line: int) -> tuple[float, float]:
    groups = match.groups()
    for minutes, seconds in ((groups[1], groups[2]), (groups[5], groups[6])):
        if int(minutes) > 59 or int(seconds) > 59:
            raise _fail("minutes and seconds must be below 60", line)
    start = _seconds(groups[0], groups[1], groups[2], groups[3])
    end = _seconds(groups[4], groups[5], groups[6], groups[7])
    if end < start:
        raise _fail("cue ends before it starts", line)
    return start, end


def _parse_srt(lines: list[str]) -> list[Utterance]:
    utterances: list[Utterance] = []
    count = len(lines)
    i = 0
    while i < count:
        if not lines[i].strip():
            i += 1
            continue
        index_line = lines[i].strip()
        if not _SRT_INDEX.fullmatch(index_line):
            raise _fail("expected a cue index", i + 1, index_line)
        i += 1
        timing = lines[i].strip() if i < count else ""
        match = _SRT_TIME.fullmatch(timing)
        if match is None:
            raise _fail("invalid timing line", i + 1, timing)
        start, end = _timing(match, i + 1)
        i += 1
        body: list[str] = []
        while i < count and lines[i].strip():
            body.append(lines[i].strip())
            i += 1
        text = " ".join(body)
        if text:
            utterances.append(Utterance(None, start, end, text))
    return utterances


def _is_keyword(head: str, keyword: str) -> bool:
    return head == keyword or head.startswith((keyword + " ", keyword + "\t"))


def _parse_vtt(lines: list[str]) -> list[Utterance]:
    header = lines[0].rstrip()
    if not _is_keyword(header, "WEBVTT"):
        raise _fail("missing WEBVTT header", 1, header)
    utterances: list[Utterance] = []
    count = len(lines)
    i = 1
    while i < count and lines[i].strip():
        i += 1
    while i < count:
        if not lines[i].strip():
            i += 1
            continue
        first = i
        block: list[str] = []
        while i < count and lines[i].strip():
            block.append(lines[i].strip())
            i += 1
        head = block[0]
        if any(_is_keyword(head, word) for word in ("NOTE", "STYLE", "REGION")):
            continue
        offset = 0 if "->" in head else 1
        if offset >= len(block):
            raise _fail("cue has no timing line", first + 1, head)
        match = _VTT_TIME.fullmatch(block[offset])
        if match is None:
            raise _fail("invalid timing line", first + offset + 1, block[offset])
        start, end = _timing(match, first + offset + 1)
        rest_start = offset + 1
        utterance = _vtt_cue(block[rest_start:], start, end)
        if utterance is not None:
            utterances.append(utterance)
    return utterances


def _vtt_cue(text_lines: list[str], start: float, end: float) -> Utterance | None:
    joined = " ".join(text_lines)
    voice = _VOICE.search(joined)
    speaker = voice.group(1).strip() if voice else None
    body = html.unescape(" ".join(_TAG.sub("", joined).split()))
    if not body:
        return None
    return Utterance(speaker or None, start, end, body)
