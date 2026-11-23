# Ticket 012: Sync glon/__init__.py version to 0.1.30

- **ID**: ticket-012
- **Owner**: agent:antigravity
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-11-23

## Goal and scope

SESSION_EXECUTION_AUTHORIZATION: Explicit user request in active session to synchronize `glon/__init__.py` `__version__` from `0.1.28` to `0.1.30` (matching `VERSION` and `pyproject.toml`) to resolve `PY011` and unblock PyPI publication of `glon 0.1.30`.

## Acceptance criteria

- [x] AC-01: `glon/__init__.py` declares `__version__ = "0.1.30"` matching `VERSION` and `pyproject.toml`.
- [x] AC-02: `pytest -q` and `./project/governance-check.sh` pass.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-antigravity.md](ai-antigravity.md)
