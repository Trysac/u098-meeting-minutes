# meeting-minutes

[![PyPI version](https://img.shields.io/pypi/v/trysac-meeting-minutes)](https://pypi.org/project/trysac-meeting-minutes/)
[![License: MIT](https://img.shields.io/pypi/l/trysac-meeting-minutes)](LICENSE)
[![CI](https://github.com/Trysac/u098-meeting-minutes/actions/workflows/ci.yml/badge.svg)](https://github.com/Trysac/u098-meeting-minutes/actions/workflows/ci.yml)

Turn meeting transcripts into validated minutes with a summary, decisions and action items with owner and due date, through an LLM port.

## Problem

After a meeting someone must write the minutes. LLM summaries can invent owners, drop decisions, return malformed JSON and follow instructions embedded in the transcript itself. This library parses transcripts (plain text, SubRip and WebVTT), calls any LLM through a small port, validates the reply against a fixed structure and checks that each item has evidence in the transcript. Items without evidence are moved to an `unverified` list instead of being trusted.

## Install

```sh
pip install trysac-meeting-minutes
# or
uv add trysac-meeting-minutes
```

Requires Python 3.10 or newer. No runtime dependencies.

## Usage

```python
from datetime import date
from meeting_minutes import RecordedLLM, generate_minutes, parse_transcript, render_markdown

utterances = parse_transcript("Ana: Ship on Friday.\nBen: Ana writes the notes.", "plain")
reply = '{"summary": "Ship on Friday.", "decisions": [{"text": "Ship on Friday", "evidence_s": [0.0]}], "action_items": [{"task": "Write the notes", "owner": "Ana", "due": "next Friday", "evidence_s": [1.0]}], "open_questions": []}'
minutes = generate_minutes(utterances, RecordedLLM([reply]), meeting_date=date(2026, 11, 5))
print(render_markdown(minutes))
```

## Public API

Import everything from `meeting_minutes`.

- `parse_transcript(text, fmt, *, max_input_chars=2_000_000) -> list[Utterance]`: `fmt` is `'plain'`, `'srt'` or `'vtt'`. Plain lines use `Speaker: text`, and times are the 0-based line index. A BOM and CRLF line endings are accepted.
- `generate_minutes(utterances, llm, *, meeting_date, attendees=(), max_chars=12_000, max_chunks=20, max_repairs=1, max_tokens=2000, on_event=None) -> Minutes`: splits the transcript into chunks, calls the LLM, validates the JSON reply and repairs it at most `max_repairs` times. Owners must match an attendee or a speaker, otherwise they become `None` with `owner_unverified=True`. Items whose evidence lies outside every utterance interval go to `Minutes.unverified`.
- `resolve_relative_date(text, today) -> date | None`: supports `today`, `tomorrow`, `this WEEKDAY`, `next WEEKDAY`, `in N days`, `in N weeks` and ISO `YYYY-MM-DD`. Returns `None` for anything else.
- `render_markdown(minutes) -> str`: renders the minutes as Markdown, collapsing each value to one line.
- Data types: `Utterance`, `Minutes`, `Decision`, `ActionItem` (frozen dataclasses).
- LLM port: `LLMPort` (a Protocol with `complete(messages, *, max_tokens) -> str`), `Message`, `RecordedLLM` (replays fixed replies and records calls) and `FakeLLM` (delegates to a function). `LLMPort` exceptions propagate unchanged.
- Errors: `MinutesError` with a `code` of `transcript_parse`, `input_too_large`, `format`, `empty_transcript` or `too_many_chunks`, and optional `line` and `raw` (at most 200 characters). `RecordingExhaustedError` (a `RuntimeError`) is raised by `RecordedLLM` when its replies run out.

Limits: 2,000,000 input characters by default for parsers, 1,500 characters for the summary, 100,000 characters for a reply, 200 items per list, 1,000 characters per text, 50 evidence values per item, 500 attendees, 200 characters for a date phrase.

## Security

See [docs/SECURITY.md](docs/SECURITY.md) for the threat model, prompt-injection defences and their limits.

## Documentation

- [Architecture](docs/ARCHITECTURE.md) and [decisions](docs/decisions/)
- [Testing](docs/TESTING.md) and [security](docs/SECURITY.md)
- [Project record](docs/PROJECT.md) and [stack](docs/STACK.md)
- [Changelog](CHANGELOG.md) and [contributing guide](CONTRIBUTING.md)

## License

[MIT](LICENSE) (c) 2026 Miguel Gomez
