# meeting-minutes

[![PyPI version](https://img.shields.io/pypi/v/trysac-meeting-minutes)](https://pypi.org/project/trysac-meeting-minutes/)
[![License: MIT](https://img.shields.io/pypi/l/trysac-meeting-minutes)](LICENSE)
[![CI](https://github.com/Trysac/u098-meeting-minutes/actions/workflows/ci.yml/badge.svg)](https://github.com/Trysac/u098-meeting-minutes/actions/workflows/ci.yml)

Turn meeting transcripts into validated minutes with summary, decisions and action items with owner and due date through an LLM port

## Problem

Describe in two or three sentences the concrete problem this utility solves, who hits it, and what
they do today without it. Replace this paragraph when the first real feature lands.

## Install

```sh
pip install trysac-meeting-minutes
# or
uv add trysac-meeting-minutes
```

Requires Python 3.10 or newer. No runtime dependencies.

## Usage

```python
import meeting_minutes

# normalize() trims surrounding whitespace and lower-cases the text.
print(meeting_minutes.normalize("  Hello World "))  # -> "hello world"

# Blank input is rejected explicitly instead of returning an empty string.
try:
    meeting_minutes.normalize("   ")
except ValueError as exc:
    print(f"rejected: {exc}")
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md) and [decisions](docs/decisions/)
- [Testing](docs/TESTING.md) and [security](docs/SECURITY.md)
- [Project record](docs/PROJECT.md) and [stack](docs/STACK.md)
- [Changelog](CHANGELOG.md) and [contributing guide](CONTRIBUTING.md)

## License

[MIT](LICENSE) (c) 2026 Miguel Gomez
