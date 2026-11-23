# Ticket 013: Validate existing origin matches owner/repo before publish

- **ID**: ticket-013
- **Owner**: agent:antigravity
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-11-23

## Goal and scope

SESSION_EXECUTION_AUTHORIZATION: Remediate the advisory security finding from Validator App PR #12 review by verifying that any existing `origin` remote URL targets the expected `owner/repo` derived from `github/<owner>/<repo>` before modifying repository visibility or pushing.

## Acceptance criteria

- [x] AC-01: `_publish_to_github` fails closed when an existing `origin` URL does not match `owner/repo` (no `gh repo edit`, `git push`, or `goal -a` executed).
- [x] AC-02: Unit tests in `tests/test_cli.py`, `mypy`, and `./project/governance-check.sh` pass.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-antigravity.md](ai-antigravity.md)
