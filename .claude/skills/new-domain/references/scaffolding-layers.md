# Domain Scaffolding Layer Details

## Reference
- Follow `src/user/` exactly. Read the corresponding user file before creating each file and replicate the pattern.
- For **Base class import paths, Generic signatures, DI patterns**,
  refer to `.claude/skills/_shared/project-dna.md`.

## Layer 1: Domain (Absolutely no infrastructure dependencies)

1. `src/{name}/__init__.py` — empty file
2. `src/{name}/domain/__init__.py` — empty file
3. `src/{name}/domain/dtos/{name}_dto.py`
   - `from pydantic import BaseModel, Field`
   - `class {Name}DTO(BaseModel)` — id, user-defined fields, created_at, updated_at
   - Use `Field(..., description="...")` for all fields
4. `src/{name}/domain/protocols/{name}_repository_protocol.py`
   - `from src._core.domain.protocols.repository_protocol import BaseRepositoryProtocol`
   - Generic: `BaseRepositoryProtocol[{Name}DTO]` (see project-dna.md section 3)
   - `class {Name}RepositoryProtocol(BaseRepositoryProtocol[{Name}DTO]): pass`
5. `src/{name}/domain/services/{name}_service.py`
   - `from src._core.domain.services.base_service import BaseService`
   - `class {Name}Service(BaseService[{Name}DTO])` — BaseService provides all CRUD delegation methods
   - CRUD methods (create_data, get_datas, get_data_by_data_id, etc.) are inherited from BaseService
   - Override methods only when custom business logic is needed
6. `src/{name}/domain/exceptions/{name}_exceptions.py`
   - `from src._core.exceptions.base_exception import BaseCustomException`
   - `{Name}NotFoundException(status_code=404, error_code="{NAME}_NOT_FOUND")`
   - `{Name}AlreadyExistsException(status_code=409, error_code="{NAME}_ALREADY_EXISTS")`
7. `src/{name}/domain/events/{name}_events.py`
   - `from src._core.domain.events.domain_event import DomainEvent`
   - `{Name}Created(DomainEvent)` — event_type="{name}.created", {name}_id
   - `{Name}Updated(DomainEvent)` — event_type="{name}.updated", {name}_id
   - `{Name}Deleted(DomainEvent)` — event_type="{name}.deleted", {name}_id

## Layer 2: Application (Optional — only when complex business logic exists)

> Do not create UseCases for basic CRUD domains.
> BaseService provides all CRUD delegation including pagination, so Router -> Service direct injection is sufficient.
> Add UseCases only when combining multiple Services or when complex business workflows are needed.

8. `src/{name}/application/__init__.py` — empty file (create only when adding UseCase)
9. `src/{name}/application/use_cases/{name}_use_case.py` — **create only when complex logic exists**
   - `__init__(self, {name}_service: {Name}Service)`
   - Handles complex workflows such as combining multiple Services, transaction orchestration, etc.

## Layer 3: Infrastructure

10. `src/{name}/infrastructure/__init__.py` — empty file
11. `src/{name}/infrastructure/database/__init__.py` — empty file
12. `src/{name}/infrastructure/database/models/{name}_model.py`
    - `from src._core.infrastructure.database.database import Base`
    - `class {Name}Model(Base)` — SQLAlchemy 2.0 `Mapped[Type]` + `mapped_column()`
    - `__tablename__ = "{name}"`
    - Use `func.now()` for `created_at`, `updated_at`
13. `src/{name}/infrastructure/repositories/{name}_repository.py`
    - `from src._core.infrastructure.database.base_repository import BaseRepository`
    - Generic: `BaseRepository[{Name}DTO]` (see project-dna.md section 3)
    - `class {Name}Repository(BaseRepository[{Name}DTO])`
    - `__init__` signature: refer to **project-dna.md section 3** "BaseRepository.__init__"
    - `super().__init__(database=database, model={Name}Model, return_entity={Name}DTO)`
14. `src/{name}/infrastructure/di/{name}_container.py`
    - DI pattern: refer to **project-dna.md section 5**
    - `class {Name}Container(containers.DeclarativeContainer)`
    - `core_container = providers.DependenciesContainer()`
    - Repository = `providers.Singleton`, Service = `providers.Factory`
    - Do not create UseCase provider by default (add only when complex logic is needed)

## Layer 4: Interface

15. `src/{name}/interface/__init__.py` — empty file
16. `src/{name}/interface/server/dtos/{name}_dto.py`
    - `from src._core.application.dtos.base_response import BaseResponse`
    - `from src._core.application.dtos.base_request import BaseRequest`
    - `{Name}Response(BaseResponse)` — exclude sensitive fields
    - `Create{Name}Request(BaseRequest)` — creation fields
    - `Update{Name}Request(BaseRequest)` — all fields Optional (`| None = None`)
    - **Multiple inheritance absolutely prohibited**
17. `src/{name}/interface/server/routers/{name}_router.py`
    - Router pattern: refer to **project-dna.md section 9**
    - `router = APIRouter()`
    - CRUD endpoints: POST /{name}, POST /{name}s, GET /{name}s, GET /{name}/{id}, PUT /{name}/{id}, DELETE /{name}/{id}
    - `@inject` + `Depends(Provide[{Name}Container.{name}_service])`
    - Conversion Patterns: refer to **project-dna.md section 6**
    - Return: `SuccessResponse(data=...)`
18. `src/{name}/interface/server/bootstrap/{name}_bootstrap.py`
    - `create_{name}_container()` — `wire(packages=["src.{name}.interface.server.routers"])`
    - `setup_{name}_routes(app)` — `app.include_router(prefix="/v1", tags=["{name}"])`
    - `setup_{name}_admin(app, database)` — Admin view registration
    - `bootstrap_{name}_domain(app, database, {name}_container)`
19. `src/{name}/interface/admin/views/{name}_view.py`
    - `from sqladmin import ModelView`
    - `class {Name}View(ModelView, model={Name}Model)`
20. `src/{name}/interface/worker/tasks/{name}_test_task.py`
    - `@broker.task(task_name=f"{settings.task_name_prefix}.{name}.test")`
    - Requires `from src._core.config import settings` import
    - `@inject` + `Provide[{Name}Container.{name}_service]`
    - `**kwargs` -> `{Name}DTO.model_validate(kwargs)`
21. `src/{name}/interface/worker/bootstrap/{name}_bootstrap.py`
    - `wire(modules=[{name}_test_task])`
    - Function name: `bootstrap_{name}_domain` (unified convention with server)

## Layer 5: App Wiring (Automatic — no manual registration needed)

> `discover_domains()` in `src/_core/infrastructure/discovery.py`
> automatically detects `src/{name}/infrastructure/di/{name}_container.py`.
> The `DynamicContainer` factory functions in Server/Worker dynamically register these,
> so there is no need to modify `container.py` or `bootstrap.py`.
>
> Auto-discovery conditions:
> - `src/{name}/__init__.py` exists
> - `src/{name}/infrastructure/di/{name}_container.py` exists
> - Directory name does not start with `_` or `.`

## Layer 5: Tests

22. `tests/factories/{name}_factory.py` — `make_{name}_dto()`, `make_create_{name}_request()`
23. `tests/unit/{name}/domain/test_{name}_service.py` — MockRepository + CRUD tests
24. `tests/unit/{name}/application/test_{name}_use_case.py` — **only when UseCase exists** MockService + tests
25. `tests/integration/{name}/infrastructure/test_{name}_repository.py` — uses test_db fixture
