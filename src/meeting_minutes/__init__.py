"""Turn meeting transcripts into validated minutes through an LLM port."""

from __future__ import annotations

import logging

from .dates import resolve_relative_date
from .errors import MinutesError
from .generate import generate_minutes
from .llm import FakeLLM, LLMPort, Message, RecordedLLM, RecordingExhaustedError
from .models import ActionItem, Decision, Minutes, Utterance
from .parsing import parse_transcript
from .render import render_markdown

__all__ = [
    "ActionItem",
    "Decision",
    "FakeLLM",
    "LLMPort",
    "Message",
    "Minutes",
    "MinutesError",
    "RecordedLLM",
    "RecordingExhaustedError",
    "Utterance",
    "__version__",
    "generate_minutes",
    "parse_transcript",
    "render_markdown",
    "resolve_relative_date",
]

__version__ = "0.1.0"

logging.getLogger(__name__).addHandler(logging.NullHandler())
