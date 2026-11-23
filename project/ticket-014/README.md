# Ticket 014: Release v0.1.31 and publish to PyPI via goal

- **ID**: ticket-014
- **Owner**: agent:antigravity
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-11-23

## Goal and scope

SESSION_EXECUTION_AUTHORIZATION: Explicit user request in active session to release `glon` v0.1.31 (including `ticket-013` origin validation hardening) and publish to PyPI via `goal`.

## Acceptance criteria

- [x] AC-01: Bump version to `0.1.31` in `VERSION`, `pyproject.toml`, and `glon/__init__.py`, and close merged `ticket-013`.
- [x] AC-02: `pytest -q` and `./project/governance-check.sh` pass.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-antigravity.md](ai-antigravity.md)
