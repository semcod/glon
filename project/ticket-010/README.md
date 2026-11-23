# Ticket 010: Publish current github/*/* repo via gh and goal -a

- **ID**: ticket-010
- **Owner**: agent:antigravity
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-11-23

## Goal and scope

SESSION_EXECUTION_AUTHORIZATION: Explicit user request in active session to update `semcod/glon` so that when invoked from inside a `github/*/*` directory (`glon`, `glon private`, `glon public`, `glon publish [private|public]`), it publishes the current repository to GitHub via `gh` (defaulting to `--private`) and runs `goal -a` to publish to PyPI and other configured registries.

## Acceptance criteria

- [x] AC-01: Detecting `github/<owner>/<repo>` from `cwd` works for both default `~/github/*/*` and nested subdirectories.
- [x] AC-02: `glon` (no URL arg inside `github/*/*`), `glon private`, and `glon public` initialize Git if needed, publish/update visibility on GitHub via `gh` (default `private`), and run `goal -a`.
- [x] AC-03: `./project/governance-check.sh`, `pytest -q`, and `mypy glon` pass.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-antigravity.md](ai-antigravity.md)
