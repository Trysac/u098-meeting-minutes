# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Add `meeting_minutes`: transcript parsers (plain, SRT, WebVTT), an `LLMPort` with `RecordedLLM`/`FakeLLM`, validated minutes generation with chunking, repair, prompt-injection escaping and evidence/owner checks, relative-date resolution and Markdown rendering.
- Initial project structure from the factory utility template.
