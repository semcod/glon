# Changelog for ticket-010

- Added `detect_github_repo_from_cwd` and `publish_repository` in `glon/cli.py` so `glon`, `glon private`, `glon public`, and `glon publish [private|public]` inside a `github/<owner>/<repo>` folder initialize Git if needed, publish/update repository visibility on GitHub via `gh` (default `private`), and invoke `goal -a` for PyPI and other registries.
- Added unit tests in `tests/test_cli.py` covering `github/*/*` detection, `gh` + `goal -a` execution, dry-run mode, and CLI subcommands.
- Closed already-merged `ticket-007` and `ticket-008` in `project/ticket-007/README.md` and `project/ticket-008/README.md`.
