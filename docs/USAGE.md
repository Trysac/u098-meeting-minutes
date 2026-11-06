# Usage

```python
from datetime import date
from meeting_minutes import RecordedLLM, generate_minutes, parse_transcript, render_markdown

utterances = parse_transcript("Ana: Ship on Friday.\nBen: Ana writes the notes.", "plain")
reply = '{"summary": "Ship on Friday.", "decisions": [{"text": "Ship on Friday", "evidence_s": [0.0]}], "action_items": [{"task": "Write the notes", "owner": "Ana", "due": "next Friday", "evidence_s": [1.0]}], "open_questions": []}'
minutes = generate_minutes(utterances, RecordedLLM([reply]), meeting_date=date(2026, 11, 5))
print(render_markdown(minutes))
```

Replace `RecordedLLM` with an adapter implementing `LLMPort.complete(messages, *, max_tokens)`.
Adapter exceptions propagate unchanged. Errors are `MinutesError` with a stable `code`:
`transcript_parse`, `input_too_large`, `format`, `empty_transcript`, `too_many_chunks`.

Use `on_event` to observe the stages (`extract`, `merge`) without seeing transcript or reply text.
See `docs/SECURITY.md` for the threat model.
