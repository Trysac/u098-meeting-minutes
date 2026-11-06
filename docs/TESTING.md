# Testing

## Running

```sh
uv run pytest --cov=meeting_minutes   # tests with coverage report
uv run python scripts/check.py      # every gate, as CI and the factory run it
```

## Policy

- Branch coverage of `src/meeting_minutes` must stay at or above 80 %; the gate fails below it.
- Tests exercise the public API (`import meeting_minutes`) and assert every observable effect: return values, raised exceptions, error codes and messages.
- Each bug fix starts with a failing test that reproduces it.
- Tests are deterministic: no network, no wall clock, no dependence on test order. The LLM is replaced by `RecordedLLM` or `FakeLLM`.

## Behaviours covered

The acceptance checks for this library cover:

- Parsing: golden utterance lists for plain, SRT and WebVTT inputs (the WebVTT fixture includes a NOTE block, a cue id and cue settings). A malformed SRT timing line raises `transcript_parse` with the correct `line`.
- Owner checks: an owner matching no attendee or speaker becomes `None` with `owner_unverified=True`; a casefolded, accent-stripped match is kept.
- Evidence checks: an item whose evidence times all fall outside the utterance intervals is moved to `unverified`.
- Repair: with `max_repairs=1`, invalid JSON triggers exactly one repair call, then `format` is raised with `raw` of at most 200 characters.
- Chunking: 300 utterances of 100 characters with `max_chars=12_000` produce three extract calls and one merge call.
- Dates: `next Friday`, `this Friday`, `next Monday`, `in 2 weeks` and an unknown phrase resolve as specified.
- Prompt injection: a transcript containing `</transcript>` yields one closing tag in the user message, and the system message contains the fixed instruction sentence.
- Events and limits: `on_event` payloads contain only the keys `stage`, `chunk`, `attempt` and `error_codes`; input above `max_input_chars` raises `input_too_large`.

## Layout

The test file names are not listed in the material this document was written from. Check the `tests/` directory in the repository for the current files before adding tests.
