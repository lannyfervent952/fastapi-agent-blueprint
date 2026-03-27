# 010. Systematizing Code Quality Tools

- Status: Superseded by [012](012-ruff-migration.md)
- Date: 2025-10-15
- Related Issues: #34, #41
- Related PRs: #42
- Related Commits: `186c0f1`, `2463f02`

## Background

In the early stages of the project, only basic pre-commit configuration existed.
As the team grew and the codebase expanded,
we wanted to tighten code conventions to maintain consistency.

## Problem

### 1. Loose Code Conventions

The existing pre-commit configuration was minimal,
creating a structure where time could be spent on style-related discussions during PR reviews.
We wanted to delegate to tools anything that could be automated.

### 2. Maintaining Unnecessary Practices

Unnecessary `# -*- coding: utf-8 -*-` headers were included in every file in the Python 3.x environment.
Since Python 3 defaults to UTF-8 encoding, this header is meaningless.

## Decision

### Major Overhaul of pre-commit Configuration

`.pre-commit-config.yaml` was significantly strengthened (commit `186c0f1`).

Key changes:
- **Bulk removal of existing UTF-8 encoding headers**: Removed `# -*- coding: utf-8 -*-` from 40 files
- **Strengthened formatting tools**: trailing whitespace, end-of-file fixer, mixed line ending, etc.
- **Added static analysis**: import sorting, type checking, etc.

### Introduced mypy in Manual Mode

mypy was registered in pre-commit but configured with `--hook-stage manual`.

```yaml
# .pre-commit-config.yaml
- repo: https://github.com/pre-commit/mirrors-mypy
  hooks:
    - id: mypy
      # Manual execution: pre-commit run --hook-stage manual mypy
```

- Running automatically on every commit would be slow and interrupt development flow
- Run manually when needed via `pre-commit run --hook-stage manual mypy`
- Can be run automatically in CI

## Rationale

| Criterion | Minimal pre-commit | Strengthened pre-commit |
|-----------|-------------------|------------------------|
| Style discussions | Manual during PR review | Eliminated via auto-formatting |
| Code consistency | Dependent on individual style | Enforced by tools |
| Unnecessary code | UTF-8 headers retained | Bulk removed |
| Type checking | None | mypy (manual mode) |

1. Automate code conventions with tools as much as possible, so reviews can focus on logic
2. Python 3 defaults to UTF-8, so encoding headers are unnecessary boilerplate
3. mypy was introduced in manual mode to balance development speed with type safety
