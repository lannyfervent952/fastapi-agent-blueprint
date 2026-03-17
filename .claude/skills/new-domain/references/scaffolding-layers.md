# 도메인 스캐폴딩 Layer 상세

## 레퍼런스
`src/user/`를 정확히 따른다. 각 파일 생성 전에 해당 user 파일을 읽고 패턴을 복제한다.

## Layer 1: Domain (infrastructure 의존성 절대 금지)

1. `src/{name}/__init__.py` — 빈 파일
2. `src/{name}/domain/__init__.py` — 빈 파일
3. `src/{name}/domain/dtos/{name}_dto.py`
   - `from pydantic import BaseModel, Field`
   - `class {Name}DTO(BaseModel)` — id, 사용자 정의 필드, created_at, updated_at
   - 모든 필드에 `Field(..., description="...")` 사용
4. `src/{name}/domain/protocols/{name}_repository_protocol.py`
   - `from src._core.domain.protocols.repository_protocol import BaseRepositoryProtocol`
   - `class {Name}RepositoryProtocol(BaseRepositoryProtocol[BaseModel, {Name}DTO, BaseModel]): pass`
5. `src/{name}/domain/services/{name}_service.py`
   - `__init__(self, {name}_repository: {Name}RepositoryProtocol)`
   - CRUD 메서드: `create_data`, `create_datas`, `get_datas_with_count`, `get_data_by_data_id`, `get_datas_by_data_ids`, `update_data_by_data_id`, `delete_data_by_data_id`, `count_datas`
   - 모든 메서드는 repository에 위임만 함
6. `src/{name}/domain/exceptions/{name}_exceptions.py`
   - `from src._core.exceptions.base_exception import BaseCustomException`
   - `{Name}NotFoundException(status_code=404, error_code="{NAME}_NOT_FOUND")`
   - `{Name}AlreadyExistsException(status_code=409, error_code="{NAME}_ALREADY_EXISTS")`

## Layer 2: Application

7. `src/{name}/application/__init__.py` — 빈 파일
8. `src/{name}/application/use_cases/{name}_use_case.py`
   - `__init__(self, {name}_service: {Name}Service)`
   - Service 메서드 미러링 + `get_datas`에서 `make_pagination()` 적용
   - `from src._core.application.dtos.base_response import PaginationInfo`
   - `from src._core.common.pagination import make_pagination`

## Layer 3: Infrastructure

9. `src/{name}/infrastructure/__init__.py` — 빈 파일
10. `src/{name}/infrastructure/database/__init__.py` — 빈 파일
11. `src/{name}/infrastructure/database/models/{name}_model.py`
    - `from src._core.infrastructure.database.database import Base`
    - `class {Name}Model(Base)` — SQLAlchemy 2.0 `Mapped[Type]` + `mapped_column()`
    - `__tablename__ = "{name}"`
    - `created_at`, `updated_at`에 `func.now()` 사용
12. `src/{name}/infrastructure/repositories/{name}_repository.py`
    - `from src._core.infrastructure.database.base_repository import BaseRepository`
    - `class {Name}Repository(BaseRepository[BaseModel, {Name}DTO, BaseModel])`
    - `super().__init__(database=database, model={Name}Model, return_entity={Name}DTO)`
13. `src/{name}/infrastructure/di/{name}_container.py`
    - `class {Name}Container(containers.DeclarativeContainer)`
    - `core_container = providers.DependenciesContainer()`
    - Repository = `providers.Singleton`, Service/UseCase = `providers.Factory`

## Layer 4: Interface

14. `src/{name}/interface/__init__.py` — 빈 파일
15. `src/{name}/interface/server/dtos/{name}_dto.py`
    - `{Name}Response(BaseResponse)` — 민감 필드 제외
    - `Create{Name}Request(BaseRequest)` — 생성 필드
    - `Update{Name}Request(BaseRequest)` — 모든 필드 Optional (`| None = None`)
    - **다중상속 절대 금지**
16. `src/{name}/interface/server/routers/{name}_router.py`
    - `router = APIRouter()`
    - CRUD 엔드포인트: POST /{name}, POST /{name}s, GET /{name}s, GET /{name}/{id}, PUT /{name}/{id}, DELETE /{name}/{id}
    - `@inject` + `Depends(Provide[{Name}Container.{name}_use_case])`
    - DTO→Response 변환: `{Name}Response(**data.model_dump(exclude={...}))`
    - 반환: `SuccessResponse(data=...)`
17. `src/{name}/interface/server/bootstrap/{name}_bootstrap.py`
    - `create_{name}_container()` — `wire(packages=["src.{name}.interface.server.routers"])`
    - `setup_{name}_routes(app)` — `app.include_router(prefix="/v1", tags=["{name}"])`
    - `setup_{name}_admin(app, database)` — Admin 뷰 등록
    - `bootstrap_{name}_domain(app, database, {name}_container)`
18. `src/{name}/interface/admin/views/{name}_view.py`
    - `from sqladmin import ModelView`
    - `class {Name}View(ModelView, model={Name}Model)`
19. `src/{name}/interface/worker/tasks/{name}_test_task.py`
    - `@broker.task(task_name="{project-name}.{name}.test")`
    - `@inject` + `Provide[{Name}Container.{name}_use_case]`
    - `**kwargs` → `{Name}DTO.model_validate(kwargs)`
20. `src/{name}/interface/worker/bootstrap/{name}_bootstrap.py`
    - `wire(modules=[{name}_test_task])`

## Layer 5: 앱 와이어링

21. `src/_apps/server/di/container.py`에 추가:
    - `{name}_container = providers.Container({Name}Container, core_container=core_container)`
22. `src/_apps/server/bootstrap.py`에 추가:
    - `from src.{name}.interface.server.bootstrap.{name}_bootstrap import bootstrap_{name}_domain`
    - `bootstrap_{name}_domain(app=app, database=..., {name}_container=server_container.{name}_container)`

## Layer 6: 테스트

23. `tests/factories/{name}_factory.py` — `make_{name}_dto()`, `make_create_{name}_request()`
24. `tests/unit/{name}/domain/test_{name}_service.py` — MockRepository + CRUD 테스트
25. `tests/unit/{name}/application/test_{name}_use_case.py` — MockService + 페이지네이션 테스트
26. `tests/integration/{name}/infrastructure/test_{name}_repository.py` — test_db 픽스처 사용
