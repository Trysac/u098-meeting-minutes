"""Tests for parse_transcript."""

from __future__ import annotations

import pytest

from meeting_minutes import MinutesError, Utterance, parse_transcript

PLAIN = "Alice: Let us ship on Friday.\nBob: Agreed.\n\nhttp://x is the link\nNo speaker here"

PLAIN_GOLDEN = [
    Utterance("Alice", 0.0, 0.0, "Let us ship on Friday."),
    Utterance("Bob", 1.0, 1.0, "Agreed."),
    Utterance(None, 3.0, 3.0, "http://x is the link"),
    Utterance(None, 4.0, 4.0, "No speaker here"),
]

SRT = """\
1
00:00:01,000 --> 00:00:02,500
Hello team.

2
00:01:00,000 --> 00:01:03,250
Line one
line two
"""

SRT_GOLDEN = [
    Utterance(None, 1.0, 2.5, "Hello team."),
    Utterance(None, 60.0, 63.25, "Line one line two"),
]

VTT = """\
WEBVTT - demo

NOTE this is a comment
second line

STYLE
::cue { color: red }

intro
00:00:01.000 --> 00:00:02.000 align:start
<v Alice>Hello <b>team</b>.</v>

00:03.000 --> 00:04.500
Plain cue &amp; more

01:00:00.000 --> 01:00:01.000
<v.loud Bob Smith>Late</v>
"""

VTT_GOLDEN = [
    Utterance("Alice", 1.0, 2.0, "Hello team."),
    Utterance(None, 3.0, 4.5, "Plain cue & more"),
    Utterance("Bob Smith", 3600.0, 3601.0, "Late"),
]


def test_plain_golden() -> None:
    assert parse_transcript(PLAIN, "plain") == PLAIN_GOLDEN


def test_srt_golden() -> None:
    assert parse_transcript(SRT, "srt") == SRT_GOLDEN


def test_vtt_golden() -> None:
    assert parse_transcript(VTT, "vtt") == VTT_GOLDEN


@pytest.mark.parametrize(
    ("text", "fmt", "golden"),
    [(PLAIN, "plain", PLAIN_GOLDEN), (SRT, "srt", SRT_GOLDEN), (VTT, "vtt", VTT_GOLDEN)],
)
def test_bom_and_crlf_are_accepted(text: str, fmt: str, golden: list[Utterance]) -> None:
    decorated = "\ufeff" + text.replace("\n", "\r\n")
    assert parse_transcript(decorated, fmt) == golden  # type: ignore[arg-type]


def test_srt_bad_timing_line_reports_line_three() -> None:
    text = "\n1\n00:00:01,000 -> 00:00:02,000\nHi"
    with pytest.raises(MinutesError) as info:
        parse_transcript(text, "srt")
    assert info.value.code == "transcript_parse"
    assert info.value.line == 3


@pytest.mark.parametrize(
    ("text", "fmt", "line"),
    [
        ("x\n00:00:01,000 --> 00:00:02,000\nHi", "srt", 1),
        ("1\n00:00:00,000 --> 00:00:01,000\nHi\n\n2\nHello", "srt", 6),
        ("1", "srt", 2),
        ("1\n00:00:05,000 --> 00:00:01,000\nHi", "srt", 2),
        ("1\n00:61:00,000 --> 00:61:01,000\nHi", "srt", 2),
        ("NOPE\n\n00:00:01.000 --> 00:00:02.000\nHi", "vtt", 1),
        ("", "vtt", 1),
        ("WEBVTT\n\n00:00:01.000 -> 00:00:02.000\nHi", "vtt", 3),
        ("WEBVTT\n\ncue1", "vtt", 3),
        ("WEBVTT\n\n00:00:02.000 --> 00:00:01.000\nHi", "vtt", 3),
        ("WEBVTT\n\nid\nnot a timing\nHi", "vtt", 4),
    ],
)
def test_parse_errors_carry_the_line(text: str, fmt: str, line: int) -> None:
    with pytest.raises(MinutesError) as info:
        parse_transcript(text, fmt)  # type: ignore[arg-type]
    assert info.value.code == "transcript_parse"
    assert info.value.line == line
    assert len(str(info.value)) < 300


def test_error_message_quotes_at_most_100_characters_of_input() -> None:
    with pytest.raises(MinutesError) as info:
        parse_transcript("z" * 500, "srt")
    assert "z" * 101 not in str(info.value)


def test_unsupported_format() -> None:
    with pytest.raises(MinutesError) as info:
        parse_transcript("a", "docx")  # type: ignore[arg-type]
    assert info.value.code == "transcript_parse"


@pytest.mark.parametrize(
    ("text", "fmt"),
    [
        ("", "plain"),
        ("\n  \n", "plain"),
        ("1\n00:00:00,000 --> 00:00:01,000\n", "srt"),
        ("WEBVTT\n", "vtt"),
    ],
)
def test_empty_transcripts(text: str, fmt: str) -> None:
    with pytest.raises(MinutesError) as info:
        parse_transcript(text, fmt)  # type: ignore[arg-type]
    assert info.value.code == "empty_transcript"


def test_input_size_limit() -> None:
    assert parse_transcript("a" * 10, "plain", max_input_chars=10)
    with pytest.raises(MinutesError) as info:
        parse_transcript("a" * 11, "plain", max_input_chars=10)
    assert info.value.code == "input_too_large"
    with pytest.raises(MinutesError) as info:
        parse_transcript("a" * 11, "nonsense", max_input_chars=10)  # type: ignore[arg-type]
    assert info.value.code == "input_too_large"


@pytest.mark.parametrize(
    ("line", "speaker", "text"),
    [
        ("Alice: a: b", "Alice", "a: b"),
        ("  Alice :  hi  ", "Alice", "hi"),
        ("Alice:no space", None, "Alice:no space"),
        ("10:30 meeting", None, "10:30 meeting"),
        ("Note:", None, "Note:"),
        (": hi", None, ": hi"),
        ("x" * 40 + ": hi", "x" * 40, "hi"),
        ("x" * 41 + ": hi", None, "x" * 41 + ": hi"),
        ("http://x", None, "http://x"),
    ],
)
def test_plain_speaker_rules(line: str, speaker: str | None, text: str) -> None:
    assert parse_transcript(line, "plain") == [Utterance(speaker, 0.0, 0.0, text)]


def test_vtt_unclosed_tags_do_not_blow_up() -> None:
    text = "WEBVTT\n\n00:00:01.000 --> 00:00:02.000\n" + "<v " * 20000 + "\n"
    result = parse_transcript(text, "vtt")
    assert len(result) == 1
    assert result[0].speaker is None


def test_vtt_cue_with_only_tags_is_skipped() -> None:
    text = "WEBVTT\n\n00:00:01.000 --> 00:00:02.000\n<b></b>\n\n00:00:03.000 --> 00:00:04.000\nHi"
    assert parse_transcript(text, "vtt") == [Utterance(None, 3.0, 4.0, "Hi")]
