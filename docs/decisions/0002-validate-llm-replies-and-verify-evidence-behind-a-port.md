# Validate LLM replies and verify evidence behind a port

Status: accepted (generated, pending human review)

## Context

LLM-written minutes invent owners, drop decisions, return malformed JSON and can be hijacked by instructions inside the transcript. Callers need testable code that works with any model vendor.

## Decision

The library talks to models only through a small LLMPort protocol. Transcripts are chunked by character count with a two-utterance overlap, each chunk is wrapped in escaped transcript tags under a fixed system message, and replies are parsed with json.loads only, validated against an explicit schema with size limits, and repaired at most max_repairs times using error messages that never include the previous reply. Owners must match an attendee or speaker and items must cite times inside the transcript, otherwise they are dropped or moved to an unverified list. Everything is standard library only.

## Consequences

Results are deterministic and testable with RecordedLLM. Hostile or invalid output cannot add unverified owners or items to the minutes, and failures surface as a typed MinutesError. The cost is extra LLM calls for merge and repair, and a due phrase the model words unusually resolves to None instead of a guessed date. Prompt injection is reduced, not eliminated; docs/SECURITY.md states this.
