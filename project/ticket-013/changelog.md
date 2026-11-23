# Changelog for ticket-013

- Validated existing `origin` remote URL against path-derived `owner/repo` in `glon/cli.py` before calling `gh repo edit` or `git push`.
- Added unit tests for mismatched and case-insensitive matching origins in `tests/test_cli.py`.
- Closed already-merged `ticket-012` in `project/ticket-012/README.md`.
