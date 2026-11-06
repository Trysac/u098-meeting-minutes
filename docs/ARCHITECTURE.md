# Architecture

## Purpose

`trysac-meeting-minutes` is a small, dependency-free Python library (import name `meeting_minutes`). It turns meeting transcripts into validated minutes with a summary, decisions and action items with owner and due date, through an LLM port.

## Shape

```text
caller code --> meeting_minutes (public API in __init__.py)
                    |
                    +-- parsers (parsing.py), dates (dates.py), models (models.py)
                    +-- generate.py: chunking, prompts, reply validation, repair
                    +-- llm.py: LLMPort protocol and test doubles
                    +-- render.py: Markdown output
```

- **Public API**: the names listed in `__all__` of `src/meeting_minutes/__init__.py`. Anything else is internal and may change without a major version.
- **LLM port**: the library never imports a vendor SDK. Callers pass any object with a `complete(messages, *, max_tokens)` method.
- **Errors**: invalid input raises `MinutesError` with a stable `code`, or `ValueError` for invalid limits and for `attendees` given as a string.
- **Side effects**: none beyond a logger that has only a `NullHandler`. The library does no network access and reads no files.

## Quality contract

`scripts/check.py` is the single definition of the gates; `fabrica.json` tells the factory and CI how to run it. See [TESTING.md](TESTING.md).

## Decisions

Architecture decisions are recorded in [decisions/](decisions/) as numbered ADRs.
