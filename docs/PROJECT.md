# Project record

## Objective

Turn meeting transcripts into validated minutes with a summary, decisions and action items with owner and due date, through an LLM port. The library parses transcripts, validates model replies against a fixed structure and checks that items come from the transcript.

## Scope

- In scope: the public API documented in [README.md](../README.md), typed and tested. This covers transcript parsing (plain, SRT, WebVTT), chunked minutes generation with JSON validation and one repair round, prompt-injection escaping, owner and evidence verification, relative due-date resolution and Markdown rendering.
- Out of scope: automatic speech recognition, speaker diarization, vendor LLM SDKs, a command-line interface, and anything that needs runtime dependencies or I/O without an accepted ADR.

## Timeline

| Date | Event |
|---|---|
| 2026 | Repository created from the factory utility template. |

## Effort metrics

Measured values only; a value that has not been measured stays "pending measurement".

| Metric | Value |
|---|---|
| Tokens (input / output) | 401699 / 113531 |
| Hours (human) | pending measurement |
| Cost (USD) | 0.8019 |

## Factory run u098 (measured from API usage)

| Phase | Model | Batch | Input | Output | Cache write | Cache read | Cost (USD) |
|---|---|---|---|---|---|---|---|
| generation | claude-sonnet-5-5 | yes | 2532 | 99824 | 0 | 4246 | 0.5021 |
| audit | claude-sonnet-5-5 | no | 16 | 5163 | 37947 | 197279 | 0.1663 |
| fix-1 | claude-sonnet-5-5 | no | 6 | 1399 | 7656 | 40686 | 0.0372 |
| docs | claude-haiku-5-5 | no | 156934 | 7145 | 0 | 0 | 0.0963 |

Total: $0.8019. Prices: Anthropic list prices.
