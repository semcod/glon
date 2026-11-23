# Ticket 011: Release v0.1.30 and publish to PyPI via goal

- **ID**: ticket-011
- **Owner**: agent:antigravity
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-11-23

## Goal and scope

SESSION_EXECUTION_AUTHORIZATION: Explicit user request in active session to release `glon` v0.1.30 (including `ticket-010` GitHub/goal publication feature) and publish to PyPI via `goal`.

## Acceptance criteria

- [x] AC-01: Bump version to `0.1.30` in `VERSION` and `pyproject.toml`, close merged `ticket-010`.
- [x] AC-02: `./project/governance-check.sh` and `pytest -q` pass.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-antigravity.md](ai-antigravity.md)
