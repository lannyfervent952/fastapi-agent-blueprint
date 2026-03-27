# 008. Deployment Environment Separation and Configuration Management

- Status: Accepted
- Date: 2025-09-15
- Related Issues: #26, #38
- Related PRs: #30
- Related Commits: `abe8a6f`, `21fd076`

## Background

As the project prepared for production deployment, settings that needed to behave differently per environment emerged.
In particular, there was a security issue where Swagger docs and error messages were exposed as-is in production.

## Problem

### 1. Swagger Documentation Exposed in Production

Without distinguishing between development and production environments, Swagger UI (`/docs-swagger`) and ReDoc (`/docs-redoc`) were always exposed.
When API documentation is publicly accessible in production, internal information such as endpoint structure, parameters, and response formats is revealed.

### 2. Indiscriminate Error Message Exposure

When errors occurred, stack traces and detailed error information were returned to clients regardless of environment,
creating a security issue where internal implementation details were exposed in production.

### 3. Configuration File Management Approach

Configuration was previously managed via `config.yml`,
which required a separate YAML parser and could not benefit from IDE auto-completion or type validation.

## Decision

### Introduced pydantic-settings Based Environment Configuration

Removed `config.yml` and created a `Settings` class using `pydantic-settings`.

```python
# src/_core/config.py (commit abe8a6f)
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    env: str = "local"
    # Control docs URL per environment
    # local/dev: Swagger UI exposed
    # prod: None (hidden)
```

### Per-Environment API Documentation Control

```python
# src/app.py
settings = Settings()
app = FastAPI(
    docs_url="/docs-swagger" if settings.env != "prod" else None,
    redoc_url="/docs-redoc" if settings.env != "prod" else None,
)
```

### Per-Environment Error Message Control

The ExceptionMiddleware was modified to determine whether to include error traces based on the environment.

## Rationale

| Criterion | config.yml | pydantic-settings |
|-----------|-----------|-------------------|
| Type validation | None (strings) | Automatic type conversion/validation |
| IDE support | None | Auto-completion, type hints |
| Env variable binding | Requires separate code | Automatic binding |
| Parser dependency | PyYAML required | Not needed (built into Pydantic) |
| Management format | `.yml` file | `.py` file (same as code) |

1. **Security was the primary motivation**: Per-environment control of docs exposure and error message exposure in production
2. Managing settings as `.py` files enables management with the same tools as code (IDE, linter, type checker)
3. `pydantic-settings` automatically binds environment variables, aligning with the 12-Factor App principles
