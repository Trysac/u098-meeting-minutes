# Security

This document is the threat model of `trysac-meeting-minutes`. To report a vulnerability see the `SECURITY.md` file in the repository root.

## Threat model

The library turns a transcript into minutes by calling a language model through the `LLMPort` protocol. Two inputs are untrusted: the transcript (any meeting participant can say anything) and the model reply (models invent owners, drop structure or return malformed JSON).

### Defended

- **Prompt injection from the transcript**: the fixed system message states that text inside `<transcript>` tags is data whose instructions must be ignored. The user message wraps each chunk in `<transcript>...</transcript>`, and every `<` that starts `</transcript` (any case), including in speaker names and attendees, is replaced by `&lt;`, so the transcript cannot close the data block. The merge call wraps the partial results the same way.
- **Malformed or hostile replies**: a reply has at most 100,000 characters, and at most one surrounding code fence is stripped. Replies are parsed only by `json.loads` with non-finite constants rejected; `RecursionError` is mapped to the `format` error. Nothing is evaluated. The structure is validated with size limits: summary 1-1500 characters, at most 200 entries per list, 1000 characters per text, 50 evidence values per item.
- **Echoing hostile replies**: a repair call sends the validation errors (at most 20 `path: message` lines) and never the previous reply.
- **Invented owners**: owners must match an attendee or a speaker after casefolding and accent stripping. Otherwise the owner becomes `None` and `owner_unverified` is `True`.
- **Unsupported items**: an item whose every `evidence_s` value lies outside all utterance intervals (inclusive) is moved to `Minutes.unverified`.
- **Guessed dates**: a due phrase that cannot be resolved becomes `None`.
- **Data leakage through events and logs**: `on_event` payloads contain only the keys `stage`, `chunk`, `attempt` and `error_codes`. The package attaches only a `NullHandler` to its logger. Error messages quote at most 200 characters of input.

### Not defended

- A model that follows instructions in the data can still produce wrong summary text, decisions or open questions. Escaping reduces this risk but cannot eliminate it. The evidence and owner checks limit what a hijacked model can add to the result, but they do not verify the summary text or the decision wording.
- Evidence checks test only that a timestamp falls inside some utterance. They do not test that the utterance supports the item's wording.
- The library does not authenticate the LLM adapter, does not manage credentials, and does not control data sent to the model provider chosen by the caller.
- Denial of service is limited but not eliminated: the parser, chunker and repair loop are bounded by the limits below, but a caller who raises the limits accepts the cost.
- Transcripts are not sanitized for personal data before they are sent to the model.

## Limits

- `max_input_chars` (default 2,000,000) for parsers.
- `max_chars` (default 12,000) per chunk and `max_chunks` (default 20) for chunking; more chunks raise `too_many_chunks`.
- `max_repairs` (default 1) repair calls per chunk.
- 500 attendees; 200 characters for date phrases.
- A reply cap of 100,000 characters.

Violations raise `MinutesError` with a stable `code`.
