# 006. Migration to Per-Domain Layered Architecture

- Status: Accepted
- Date: 2025-07-16 ~ 2025-08-24
- Related issues: #19, #10, #9
- Related PRs: #20, #14, #15
- Related commits: `f59e96b`, `e248abf`, `bad7a62`, `88afd88`, `1567ec3`

## Background

In the early stages of the project, application code and domain code were separated into `src/apps/` and `src/domains/`.

```
src/
├── apps/
│   ├── monolith/app.py       # Monolith server
│   ├── gateway/app.py        # API gateway
│   └── microservices/
│       ├── user/app.py
│       └── chat/app.py
└── domains/
    ├── core/                  # Common infrastructure
    │   ├── application/
    │   ├── domain/
    │   └── infrastructure/
    └── user/
        ├── domain/
        └── server/
```

Additionally, FastAPI's routing handlers were named `controller`.

## Problem

### 1. Management Complexity of App/Domain Separation

With `apps/` and `domains/` separated, tracking down an issue in a specific feature
required navigating between two directories.
For example, to trace a problem in the user domain:
- `src/apps/microservices/user/` — app configuration
- `src/domains/user/` — business logic
- `src/domains/core/` — common infrastructure

Three locations had to be checked.

### 2. Controller Naming Inconsistency

In the FastAPI ecosystem, routing handlers are called `Router`.
Using `APIRouter` while naming the files `controller` caused confusion.

```python
# Inconsistency: using FastAPI's APIRouter while naming it controller
router = APIRouter()  # FastAPI convention: router
# Filename: user_controller.py  # Project convention: controller
```

### 3. Unnecessary Gateway App

An API gateway was created as a separate app (`apps/gateway/`),
but it was unused code in the current single-server architecture.

## Decision

The structure was improved in three stages.

### Stage 1: Rename Controller to Router (#10, 2025-07-16)

To align with FastAPI conventions, the `controllers/` directory was renamed to `routers/`, and filenames were changed to `*_router.py`.

### Stage 2: Add WebSocket Router (#9, 2025-07-16)

Along with adding WebSocket support, routers were separated by protocol:

```
routers/
├── api/           # HTTP REST routers
│   └── user/
└── websocket/     # WebSocket routers
    └── chat/
```

### Stage 3: Per-Domain Flattening (#19, 2025-08-24)

`apps/` and `domains/` were removed, and each domain was placed directly under `src/`.

```
# After: per-domain flattening
src/
├── app.py              # Main app (absorbed monolith)
├── core/               # Common infrastructure
│   ├── application/
│   ├── domain/
│   └── infrastructure/
├── user/               # user domain (app + domain unified)
│   ├── domain/
│   ├── infrastructure/
│   └── server/
└── chat/               # chat domain
    ├── domain/
    ├── infrastructure/
    └── server/
```

- Removed the gateway app (73 lines of unused code)
- Absorbed the monolith app into `src/app.py`
- Integrated microservices apps into their respective domains

## Rationale

| Criteria | apps/domains Separation (before) | Per-Domain Flattening (current) |
|----------|--------------------------------|-------------------------------|
| Code navigation | Must check 3 locations (apps, domains, core) | Just open one domain folder |
| Naming | controller (Spring convention) | router (FastAPI convention) |
| Unused code | gateway app present | Removed |
| Domain independence | App config separated from logic | Domain contains its own app config |

1. Placing domain folders at the top level enables quick navigation directly to the relevant domain folder when issues arise
2. Following FastAPI's `APIRouter` naming convention keeps framework documentation and code consistent
3. Removing unused gateway code prevents confusion
4. Although it was a large-scale refactoring involving 87 files, most changes were file moves, keeping logic changes minimal

## Follow-up

- DI container and shared infrastructure design proceeded based on this structure -> [007](007-di-container-and-app-separation.md)
- A domain auto-discovery system was later introduced, eliminating the need to modify `container.py` when adding new domains
