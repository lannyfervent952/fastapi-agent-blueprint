# 007. DI Container Layering and Interface-Specific App Separation

- Status: Accepted
- Date: 2025-09-09 ~ 2025-11-18
- Related Issues: #21, #49
- Related PRs: #23, #50
- Related Commits: `5b96e3b`, `aafdcd4`

## Background

After transitioning to a domain-based layered architecture ([006](006-ddd-layered-architecture.md)),
two problems emerged with the DI container and application configuration.

1. All domain business logic and data logic were concentrated in a single container
2. Server, Worker, and Admin all ran within the same app, making interface-specific separation impossible

## Problem

### 1. Single Container Bloat

As domains grew, a single container ended up containing all Use Cases, Services, and Repositories for every domain,
making the container itself increasingly heavy.

### 2. Circular References Between Domains

For example, the User domain needed to use functionality from the Video domain,
and the Video domain also needed to reference the User domain.
Resolving this circular dependency was difficult within a single container.

### 3. Different Requirements Per Interface

Server (API), Worker (async tasks), and Admin (management tools) each required:
- Different routers/tasks/views
- Different middleware configurations
- Shared business logic (Service, Repository)

Handling all of this in a single app loaded unnecessary dependencies.

## Decision

### Phase 1: Per-Domain Container + Top-Level ServerContainer (#21, 2025-09)

Each domain was given its own DI container,
and a top-level container (`ServerContainer`) was introduced in the `_shared/` folder to compose them.

```python
# src/_shared/infrastructure/di/server_container.py (commit 5b96e3b)
class ServerContainer(containers.DeclarativeContainer):
    core_container = providers.Container(CoreContainer)
    user_container = providers.Container(
        UserContainer, core_container=core_container
    )
```

- Domain containers were separated to manage each domain's dependencies independently
- Circular references were resolved by injecting dependencies from the parent container
- The scalability weakness of layered architecture was compensated through container layering

### Phase 2: _shared to _apps Refactoring, Interface-Specific App Separation (#49, 2025-11)

The `_shared/` folder was restructured into `_apps/` to separate Server, Worker, and Admin into distinct apps.

```
# Before (_shared structure)
src/
├── _shared/infrastructure/di/server_container.py
├── app.py              # Single app
└── celery_app.py       # Celery app (separate)

# After (_apps structure)
src/
├── _apps/
│   ├── server/         # API server
│   │   ├── app.py
│   │   ├── bootstrap.py
│   │   └── di/container.py
│   ├── worker/         # Async task worker
│   │   ├── app.py
│   │   ├── bootstrap.py
│   │   └── di/container.py
│   └── admin/          # Management tools
│       ├── app.py
│       ├── bootstrap.py
│       └── di/container.py
└── user/
    └── interface/
        ├── server/     # API routers
        └── worker/     # Worker tasks (renamed from consumer to worker)
```

Each app has its own independent container and bootstrap,
while sharing the domain's Service/Repository layers.

## Rationale

| Criterion | Single Container + Single App | Per-Domain Container + App Separation |
|-----------|-------------------------------|---------------------------------------|
| Container size | Unbounded bloat as domains grow | Isolated per domain, loads only what's needed |
| Circular references | Hard to resolve | Resolved via dependency injection from parent container |
| Business logic sharing | N/A (single app) | Server/Worker/Admin reuse the same Services |
| Management points | Few (1 app) | More (3 apps) |
| Independent deployment | Not possible | Each interface can run independently |

1. **Business logic sharing is the key benefit**: Server, Worker, and Admin can share simple CRUD code and common business logic. Since Worker and Admin need to be built separately anyway, managing them within the same architecture actually reduces management overhead.
2. **Container layering**: Compensates for the scalability weakness of layered architecture through DI containers.
3. **Increased management points are acceptable**: The number of apps grows to 3, but eliminating duplication of sharable logic provides a greater benefit.

## Follow-up

- Celery was later replaced with Taskiq ([001](001-celery-to-taskiq.md)), which also changed the Worker app structure
- consumer was renamed to worker (done together in commit `aafdcd4`)
- Domain auto-discovery system introduced in #57, eliminating the need to modify containers in `_apps/` when adding new domains
