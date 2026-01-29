# 🧬 Skill.md v2: FastAPI Layered Architecture - Complete Project DNA

> **Version**: 2.0  
> **Last Updated**: 2026-01-29  
> **Purpose**: 이 문서는 AI가 프로젝트의 모든 패턴, 규칙, 관례를 완벽히 이해하고 일관된 코드를 생성할 수 있도록 프로젝트의 완전한 DNA를 정의합니다.

---

## 📋 Table of Contents

1. [Architecture Overview (아키텍처 개요)](#1-architecture-overview-아키텍처-개요)
2. [Layer-by-Layer Guide (계층별 상세 가이드)](#2-layer-by-layer-guide-계층별-상세-가이드)
3. [Code Standards (코드 표준)](#3-code-standards-코드-표준)
4. [Common Patterns (공통 패턴)](#4-common-patterns-공통-패턴)
5. [Domain Addition Checklist (도메인 추가 체크리스트)](#5-domain-addition-checklist-도메인-추가-체크리스트)
6. [Do's and Don'ts (필수 준수사항)](#6-dos-and-donts-필수-준수사항)

---

## 1. Architecture Overview (아키텍처 개요)

### 1.1 핵심 철학

이 프로젝트는 **Generic TypeVar 기반 3계층 베이스 시스템**과 **DDD 4계층 아키텍처**를 결합한 고도로 추상화된 구조입니다.

**핵심 가치**:
- **재사용성**: 모든 CRUD 로직은 Base 클래스에서 자동 제공
- **타입 안정성**: Generic TypeVar로 컴파일 타임 타입 체크
- **계층 분리**: 각 계층은 명확한 책임과 의존성 방향 보유
- **비동기 우선**: 모든 I/O 작업은 `async/await` 패턴 사용

### 1.2 제네릭 3계층 베이스 시스템

```python
# 핵심 TypeVar 정의 (모든 계층에서 동일한 이름 사용)
CreateEntity = TypeVar("CreateEntity", bound=Entity)
ReturnEntity = TypeVar("ReturnEntity", bound=Entity)
UpdateEntity = TypeVar("UpdateEntity", bound=Entity)

# 계층별 상속 체인
BaseRepository[CreateEntity, ReturnEntity, UpdateEntity]
    ↓ 주입
BaseService[CreateEntity, ReturnEntity, UpdateEntity]
    ↓ 주입
BaseUseCase[CreateEntity, ReturnEntity, UpdateEntity]
```

**자동 제공 메서드** (각 계층에서 동일):

| Repository | Service | UseCase | 설명 |
|------------|---------|---------|------|
| `insert_data` | `create_data` | `create_data` | 단일 생성 |
| `insert_datas` | `create_datas` | `create_datas` | 복수 생성 |
| `select_datas` | `get_datas` | `get_datas` | 페이지네이션 조회 |
| `select_data_by_id` | `get_data_by_data_id` | `get_data_by_data_id` | ID 조회 |
| `select_datas_by_ids` | `get_datas_by_data_ids` | `get_datas_by_data_ids` | 복수 ID 조회 |
| `select_datas_with_count` | `get_datas_with_count` | `get_datas` (with pagination) | 데이터 + 카운트 |
| `update_data_by_data_id` | `update_data_by_data_id` | `update_data_by_data_id` | 수정 |
| `delete_data_by_data_id` | `delete_data_by_data_id` | `delete_data_by_data_id` | 삭제 |
| `count_datas` | `count_datas` | - | 전체 카운트 |

### 1.3 DDD 4계층 아키텍처

```
┌─────────────────────────────────────────────────────────────────┐
│  Interface Layer (인터페이스 계층)                                │
│  ├─ server/   : FastAPI REST API 엔드포인트                      │
│  ├─ admin/    : SQLAdmin 관리자 뷰                               │
│  └─ worker/   : Taskiq 비동기 작업 Consumer                      │
│                                                                   │
│  역할: 외부 요청 수신, DTO ↔ Entity 변환, 응답 포맷팅              │
├─────────────────────────────────────────────────────────────────┤
│  Application Layer (애플리케이션 계층)                            │
│  └─ use_cases/ : 비즈니스 유스케이스 조율                         │
│                                                                   │
│  역할: 여러 Service 조율, 트랜잭션 경계 정의, PaginationInfo 생성  │
├─────────────────────────────────────────────────────────────────┤
│  Domain Layer (도메인 계층)                                       │
│  ├─ entities/ : Pydantic 기반 불변 데이터 모델                    │
│  └─ services/ : 순수 비즈니스 로직                                │
│                                                                   │
│  역할: 핵심 비즈니스 규칙, 인프라 의존성 없음 (순수 도메인)         │
├─────────────────────────────────────────────────────────────────┤
│  Infrastructure Layer (인프라 계층)                               │
│  ├─ database/   : SQLAlchemy ORM, Repository 구현                │
│  ├─ http/       : aiohttp 외부 API 클라이언트                    │
│  ├─ storage/    : aioboto3 S3/MinIO 파일 관리                   │
│  ├─ taskiq/     : Taskiq 비동기 작업 큐                          │
│  └─ di/         : dependency-injector Container                  │
│                                                                   │
│  역할: 외부 시스템 연동, 데이터 영속성, 인프라 추상화              │
└─────────────────────────────────────────────────────────────────┘

의존성 방향: Interface → Application → Domain ← Infrastructure
```

### 1.4 프로젝트 구조

```
fastapi-layered-architecture/
├── src/
│   ├── _core/                    # 공통 인프라 (모든 도메인이 공유)
│   │   ├── application/
│   │   │   ├── dtos/             # BaseRequest, BaseResponse, ApiConfig
│   │   │   ├── routers/          # 공통 라우터 (health check, docs)
│   │   │   └── use_cases/        # BaseUseCase
│   │   ├── domain/
│   │   │   ├── entities/         # Entity (Pydantic BaseModel)
│   │   │   └── services/         # BaseService
│   │   ├── infrastructure/
│   │   │   ├── database/         # Database, BaseRepository, DatabaseConfig
│   │   │   ├── http/             # HttpClient, BaseHttpGateway
│   │   │   ├── storage/          # ObjectStorage (S3/MinIO)
│   │   │   ├── taskiq/           # TaskiqManager, CustomSQSBroker
│   │   │   └── di/               # CoreContainer
│   │   ├── middleware/           # ExceptionMiddleware
│   │   ├── exceptions/           # BaseCustomException
│   │   ├── common/               # 유틸리티 (pagination, dto_utils)
│   │   └── config.py             # Settings (환경변수 관리)
│   │
│   ├── _apps/                    # 애플리케이션 진입점
│   │   ├── server/               # FastAPI 서버
│   │   │   ├── app.py            # create_app()
│   │   │   ├── bootstrap.py      # bootstrap_app()
│   │   │   └── di/container.py   # ServerContainer
│   │   ├── worker/               # Taskiq Worker
│   │   │   ├── app.py            # Worker 진입점
│   │   │   ├── broker.py         # Broker 인스턴스
│   │   │   ├── bootstrap.py      # bootstrap_app()
│   │   │   └── di/container.py   # WorkerContainer
│   │   └── admin/                # Admin 앱 (예약됨)
│   │
│   └── {domain}/                 # 도메인별 모듈 (예: user)
│       ├── domain/
│       │   ├── entities/         # {domain}_entity.py
│       │   └── services/         # {domain}_service.py
│       ├── application/
│       │   └── use_cases/        # {domain}_use_case.py
│       ├── infrastructure/
│       │   ├── database/
│       │   │   └── models/       # {domain}_model.py
│       │   ├── repositories/     # {domain}_repository.py
│       │   └── di/               # {domain}_container.py
│       └── interface/
│           ├── server/
│           │   ├── routers/      # {domain}_router.py
│           │   ├── dtos/         # {domain}_dto.py
│           │   └── bootstrap/    # {domain}_bootstrap.py
│           ├── admin/
│           │   └── views/        # {domain}_view.py (SQLAdmin)
│           └── worker/
│               ├── tasks/        # {domain}_task.py
│               └── bootstrap/    # {domain}_bootstrap.py
│
├── migrations/                   # Alembic 마이그레이션
│   ├── env.py                    # Alembic 환경 설정
│   ├── env_utils.py              # 모델 자동 로드
│   └── versions/                 # 마이그레이션 파일
│
├── _env/                         # 환경별 설정 파일
│   ├── local.env
│   ├── dev.env
│   ├── stg.env
│   └── prod.env
│
├── alembic.ini                   # Alembic 설정
├── pyproject.toml                # 의존성 관리
├── .pre-commit-config.yaml       # 코드 품질 자동화
└── run_server_local.py           # 로컬 서버 실행
```

---

## 2. Layer-by-Layer Guide (계층별 상세 가이드)

### 2.1 Infrastructure Layer (인프라 계층)

#### **2.1.1 Database (데이터베이스)**

**핵심 컴포넌트**:
- `Database`: 비동기 연결 풀 관리 (`AsyncEngine`, `AsyncSession`)
- `BaseRepository`: Generic CRUD 자동화
- `DatabaseConfig`: 환경별 설정 (`from_env` 패턴)

**Database 클래스 패턴**:
```python
class Database:
    def __init__(self, database_user: str, database_password: str, ...):
        self.engine = create_engine(...)  # 동기 엔진 (Alembic, SQLAdmin용)
        self.async_engine = create_async_engine(...)  # 비동기 엔진
        self.async_session_factory = sessionmaker(...)
    
    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        session = None
        try:
            session = self.async_session_factory()
            yield session
        except IntegrityError:
            if session:
                await session.rollback()
            raise DatabaseException(
                status_code=400,
                message="Data integrity error",
                error_code="DB_INTEGRITY_ERROR",
            )
        except Exception as e:
            if session:
                await session.rollback()
            raise DatabaseException(
                status_code=500,
                message="Internal database error",
                error_code="DB_INTERNAL_ERROR",
            )
        finally:
            if session:
                await session.close()
```

**트랜잭션 경계**: 
- Repository의 각 메서드는 `async with self.database.session()` 블록 내에서 실행
- 자동 롤백 및 예외 처리
- **중요**: Repository 메서드는 단일 트랜잭션, 여러 Repository 조율은 UseCase에서 처리

**환경별 설정**:
```python
@classmethod
def from_env(cls, env: str) -> "DatabaseConfig":
    if env == "prod":
        return cls(echo=False, pool_size=10, max_overflow=20, pool_recycle=3600)
    return cls(echo=True, pool_size=5, max_overflow=10, pool_recycle=1800)
```

#### **2.1.2 HTTP Client (외부 API 클라이언트)**

**핵심 컴포넌트**:
- `HttpClient`: aiohttp 기반 비동기 HTTP 클라이언트
- `BaseHttpGateway`: 외부 API 통합용 추상 클래스

**HttpClient 패턴**:
```python
class HttpClient:
    def __init__(self, env: str):
        self._client_session: ClientSession | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._connector_limit = 100 if env == "prod" else 50
    
    @asynccontextmanager
    async def session(self) -> AsyncGenerator[ClientSession, None]:
        try:
            session = await self._ensure_session()
            yield session
        except aiohttp.ClientError as e:
            raise HTTPException(status_code=502, detail=f"External service error: {str(e)}")
        except TimeoutError:
            raise HTTPException(status_code=504, detail="External service timeout")
```

**BaseHttpGateway 사용 예시**:
```python
class ExternalAPIGateway(BaseHttpGateway):
    def __init__(self, http_client: HttpClient):
        super().__init__(http_client=http_client, base_url="https://api.example.com")
    
    def _get_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}"}
    
    async def get_user_data(self, user_id: int) -> dict:
        return await self._get(endpoint=f"/users/{user_id}")
```

#### **2.1.3 Object Storage (S3/MinIO)**

**핵심 컴포넌트**:
- `ObjectStorage`: aioboto3 기반 비동기 S3/MinIO 클라이언트
- `ObjectStorageClient`: aioboto3 세션 래퍼

**주요 메서드**:
```python
async def upload_file(self, file_content: bytes, key: str) -> str
async def download_file(self, key: str) -> bytes
async def delete_file(self, key: str) -> bool
async def file_exists(self, key: str) -> bool
async def generate_presigned_url(self, key: str, expires_in: int = 3600) -> str
async def list_files(self, prefix: str = "") -> list[str]
```

**예외 처리**:
```python
except ClientError as e:
    if e.response["Error"]["Code"] == "NoSuchKey":
        raise BaseCustomException(status_code=404, message=f"File not found: {key}")
    raise BaseCustomException(status_code=500, message=f"Storage operation failed: {e}")
```

#### **2.1.4 Taskiq (비동기 작업 큐)**

**핵심 컴포넌트**:
- `CustomSQSBroker`: AWS SQS 기반 Taskiq Broker
- `TaskiqManager`: 작업 전송 관리자

**Worker 앱 구조**:
```python
# src/_apps/worker/broker.py
container = CoreContainer()
broker = container.broker()

# src/_apps/worker/bootstrap.py
def bootstrap_app(app: SQSBroker) -> None:
    @app.on_event("startup")
    async def startup(state: TaskiqState):
        worker_container = WorkerContainer(core_container=container)
        bootstrap_user(app=app, user_container=worker_container.user_container)
```

**Task 정의 패턴**:
```python
# src/user/interface/worker/tasks/user_test_task.py
@broker.task(task_name="{project-name}.user.test")
@inject
async def consume_task(
    user_use_case: UserUseCase = Provide[UserContainer.user_use_case],
    **kwargs,
) -> None:
    entity = UserEntity.model_validate(kwargs)
    await user_use_case.process_user(entity=entity)
```

**Task 전송**:
```python
# Router에서 TaskiqManager 사용
await taskiq_manager.send_task(
    task_name="{project-name}.user.test",
    kwargs={"id": 1, "username": "test"}
)
```

#### **2.1.5 Dependency Injection (의존성 주입)**

**Container 계층 구조**:
```
CoreContainer (인프라 공통)
    ↓ 주입
{Domain}Container (도메인별)
    ↓ 주입
ServerContainer / WorkerContainer (앱별)
```

**CoreContainer 패턴**:
```python
class CoreContainer(containers.DeclarativeContainer):
    # Singleton: 연결 풀 재사용 (Database, HttpClient, Storage, Broker)
    database = providers.Singleton(Database, ...)
    http_client = providers.Singleton(HttpClient, ...)
    s3_storage = providers.Factory(ObjectStorage, ...)  # Factory: 요청마다 새 인스턴스
    broker = providers.Singleton(CustomSQSBroker, ...)
    taskiq_manager = providers.Singleton(TaskiqManager, broker=broker)
```

**Domain Container 패턴**:
```python
class UserContainer(containers.DeclarativeContainer):
    core_container = providers.DependenciesContainer()
    
    # Singleton: Repository (연결 풀 재사용)
    user_repository = providers.Singleton(
        UserRepository,
        database=core_container.database,
    )
    
    # Factory: Service, UseCase (요청마다 새 인스턴스)
    user_service = providers.Factory(UserService, user_repository=user_repository)
    user_use_case = providers.Factory(UserUseCase, user_service=user_service)
```

**Wiring 패턴**:
```python
# Server
user_container.wire(packages=["src.user.interface.server.routers"])

# Worker
user_container.wire(modules=[user_test_task])
```

### 2.2 Domain Layer (도메인 계층)

#### **2.2.1 Entity (엔티티)**

**Entity 기본 클래스**:
```python
class Entity(ABC, BaseModel):
    class Config:
        use_enum_values = True  # Enum을 값으로 직렬화
```

**Entity 설계 패턴** (3가지 Entity 필수):
```python
# 1. ReturnEntity: 전체 필드 (DB에서 조회된 데이터)
class UserEntity(Entity):
    id: int = Field(..., description="유저 고유 식별자")
    username: str = Field(..., max_length=20)
    email: str
    password: str
    created_at: datetime
    updated_at: datetime

# 2. CreateEntity: 생성 시 필요한 필드 (id, timestamp 제외)
class CreateUserEntity(Entity):
    username: str = Field(..., max_length=20)
    email: str
    password: str

# 3. UpdateEntity: 수정 시 필요한 필드 (id, timestamp 제외, Optional 가능)
class UpdateUserEntity(Entity):
    username: str | None = None
    email: str | None = None
    password: str | None = None
```

#### **2.2.2 Service (서비스)**

**Service 역할**:
- 순수 비즈니스 로직 구현
- Repository 메서드 호출 및 조율
- 인프라 의존성 없음 (Database, HttpClient 직접 사용 금지)

**Service 패턴**:
```python
class UserService(BaseService[CreateUserEntity, UserEntity, UpdateUserEntity]):
    def __init__(self, user_repository: UserRepository) -> None:
        super().__init__(
            base_repository=user_repository,
            create_entity=CreateUserEntity,
            return_entity=UserEntity,
            update_entity=UpdateUserEntity,
        )
    
    # 커스텀 비즈니스 로직 추가
    async def get_user_by_email(self, email: str) -> UserEntity:
        return await self.base_repository.select_data_by_email(email=email)
```

### 2.3 Application Layer (애플리케이션 계층)

#### **2.3.1 UseCase (유스케이스)**

**UseCase 역할**:
- 여러 Service 조율
- 트랜잭션 경계 정의 (복잡한 비즈니스 플로우)
- PaginationInfo 생성 (페이지네이션 메타데이터)

**UseCase 패턴**:
```python
class UserUseCase(BaseUseCase[CreateUserEntity, UserEntity, UpdateUserEntity]):
    def __init__(self, user_service: UserService) -> None:
        super().__init__(
            base_service=user_service,
            create_entity=CreateUserEntity,
            return_entity=UserEntity,
            update_entity=UpdateUserEntity,
        )
    
    # 복잡한 비즈니스 플로우 (여러 Service 조율)
    async def register_user_with_notification(
        self, entity: CreateUserEntity
    ) -> UserEntity:
        # 1. 사용자 생성
        user = await self.base_service.create_data(entity=entity)
        
        # 2. 알림 전송 (다른 Service 사용)
        # await notification_service.send_welcome_email(user.email)
        
        return user
```

#### **2.3.2 DTO (Data Transfer Object)**

**DTO 기본 클래스**:
```python
# API_CONFIG: Pydantic ConfigDict
API_CONFIG = ConfigDict(
    extra="ignore",              # 추가 필드 무시
    frozen=True,                 # 불변 객체
    populate_by_name=True,       # 별칭/원래 이름 모두 허용
    loc_by_alias=True,           # 에러 위치를 별칭으로 표시
    alias_generator=to_camel,    # snake_case → camelCase 자동 변환
    ser_json_timedelta="iso8601",
    ser_json_bytes="utf8",
)

class ApiConfig(BaseConfig):
    model_config = API_CONFIG
```

**Request DTO 패턴**:
```python
class CreateUserRequest(BaseRequest, CreateUserEntity):
    pass  # Entity 필드 상속

# Router에서 사용
@router.post("/user")
async def create_user(item: CreateUserRequest, ...):
    entity = item.to_entity(CreateUserEntity)  # DTO → Entity 변환
    data = await user_use_case.create_data(entity=entity)
    return SuccessResponse(data=UserResponse.from_entity(data))
```

### 2.4 Interface Layer (인터페이스 계층)

#### **2.4.1 Server (FastAPI REST API)**

**Router 패턴**:
```python
router = APIRouter()

@router.post(
    "/user",
    response_model=SuccessResponse[UserResponse],
    response_model_exclude={"pagination"},
)
@inject  # DI 데코레이터 필수
async def create_user(
    item: CreateUserRequest,
    user_use_case: UserUseCase = Depends(Provide[UserContainer.user_use_case]),
):
    entity = item.to_entity(CreateUserEntity)
    data = await user_use_case.create_data(entity=entity)
    return SuccessResponse(data=UserResponse.from_entity(data))
```

**Bootstrap 패턴**:
```python
def bootstrap_user_domain(
    app: FastAPI, database: Database, user_container: UserContainer
):
    # 1. Wiring (DI 연결)
    user_container.wire(packages=["src.user.interface.server.routers"])
    
    # 2. Router 등록
    app.include_router(router=user_router.router, prefix="/v1", tags=["사용자"])
    
    # 3. Admin 뷰 등록
    if database:
        admin = Admin(app=app, engine=database.engine)
        admin.add_view(UserView)
```

#### **2.4.2 Admin (SQLAdmin 관리자 뷰)**

**Admin View 패턴**:
```python
class UserView(ModelView, model=UserModel):  # type: ignore[call-arg]
    category = "유저"
    name = "유저 목록"
    column_list = [attr.key for attr in class_mapper(UserModel).column_attrs]
    
    column_labels = {
        UserModel.id: "ID",
        UserModel.username: "이름",
        UserModel.email: "이메일",
    }
    
    column_searchable_list = [UserModel.id, UserModel.username, UserModel.email]
    column_sortable_list = [UserModel.id, UserModel.username, UserModel.created_at]
```

#### **2.4.3 Worker (Taskiq 비동기 작업)**

**Task 정의 패턴**:
```python
@broker.task(task_name="{project-name}.user.test")
@inject
async def consume_task(
    user_use_case: UserUseCase = Provide[UserContainer.user_use_case],
    **kwargs,
) -> None:
    entity = UserEntity.model_validate(kwargs)
    await user_use_case.process_user(entity=entity)
```

---

## 3. Code Standards (코드 표준)

### 3.1 타입 힌팅 규칙

**필수 타입 힌팅**:
```python
# ✅ 모든 함수/메서드 시그니처
async def create_data(self, entity: CreateEntity) -> ReturnEntity:
    ...

# ✅ 클래스 속성
class Database:
    engine: Engine
    async_engine: AsyncEngine

# ✅ Optional/Union 명시 (Python 3.10+ 스타일)
s3_access_key: str | None = Field(default=None)
```

**Generic TypeVar 규칙**:
```python
# ✅ 항상 동일한 이름 사용
CreateEntity = TypeVar("CreateEntity", bound=Entity)
ReturnEntity = TypeVar("ReturnEntity", bound=Entity)
UpdateEntity = TypeVar("UpdateEntity", bound=Entity)

# ❌ 이름 변경 금지
CreateDTO = TypeVar("CreateDTO", bound=Entity)  # 금지
```

### 3.2 네이밍 컨벤션

#### **파일 네이밍**

| 계층 | 파일명 패턴 | 클래스명 패턴 |
|------|------------|--------------|
| Entity | `{domain}_entity.py` | `UserEntity`, `CreateUserEntity` |
| Model | `{domain}_model.py` | `UserModel`, `__tablename__ = "user"` |
| Repository | `{domain}_repository.py` | `UserRepository` |
| Service | `{domain}_service.py` | `UserService` |
| UseCase | `{domain}_use_case.py` | `UserUseCase` |
| Router | `{domain}_router.py` | `router = APIRouter()` |
| DTO | `{domain}_dto.py` | `UserResponse`, `CreateUserRequest` |

#### **메서드 네이밍**

| Repository | Service | UseCase |
|------------|---------|---------|
| `insert_data` | `create_data` | `create_data` |
| `select_data_by_id` | `get_data_by_data_id` | `get_data_by_data_id` |
| `update_data_by_data_id` | `update_data_by_data_id` | `update_data_by_data_id` |
| `delete_data_by_data_id` | `delete_data_by_data_id` | `delete_data_by_data_id` |

### 3.3 Import 순서

```python
# 1. 표준 라이브러리
from abc import ABC
from typing import Generic, TypeVar

# 2. 외부 라이브러리
from fastapi import APIRouter, Depends
from pydantic import Field

# 3. 로컬 모듈 (절대 경로만 사용)
from src._core.domain.entities.entity import Entity
from src.user.domain.entities.user_entity import UserEntity

# ❌ 상대 경로 금지
from ...domain.entities.entity import Entity  # 금지
```

---

## 4. Common Patterns (공통 패턴)

### 4.1 예외 처리 전략

**Repository 계층**:
```python
if not data:
    raise BaseCustomException(
        status_code=404,
        message=f"Data with ID [ {data_id} ] not found"
    )
```

**Database 계층**:
```python
except IntegrityError:
    raise DatabaseException(
        status_code=400,
        message="Data integrity error",
        error_code="DB_INTEGRITY_ERROR",
    )
```

### 4.2 Alembic 마이그레이션 워크플로우

**마이그레이션 생성**:
```bash
# alembic.ini에서 env 설정 (local, dev, stg, prod)
# [alembic]
# env = local

# 마이그레이션 파일 생성
alembic revision --autogenerate -m "Add user table"

# 마이그레이션 적용
alembic upgrade head

# 마이그레이션 롤백
alembic downgrade -1
```

**env.py 핵심 로직**:
```python
# 1. 환경 변수 로드
env = config.get_main_option("env")  # alembic.ini에서 읽음
load_dotenv(dotenv_path=f"_env/{env}.env", override=True)

# 2. 모든 도메인 모델 자동 로드
load_models()  # src/{domain}/infrastructure/database/models/ 탐색

# 3. Base.metadata 사용
target_metadata = Base.metadata
```

**중요 규칙**:
- ✅ 모든 Model은 `Base`를 상속
- ✅ `__tablename__` 명시 필수
- ✅ 마이그레이션 파일은 절대 수동 수정 금지
- ✅ `alembic.ini`의 `env` 설정 확인 필수

---

## 5. Domain Addition Checklist (도메인 추가 체크리스트)

새 도메인을 추가할 때는 아래 단계를 순서대로 진행하세요.

### **Step 1: Entity 정의**
**파일**: `src/{domain}/domain/entities/{domain}_entity.py`

```python
class UserEntity(Entity):
    id: int = Field(..., description="유저 고유 식별자")
    username: str = Field(..., max_length=20)
    created_at: datetime
    updated_at: datetime

class CreateUserEntity(Entity):
    username: str = Field(..., max_length=20)

class UpdateUserEntity(Entity):
    username: str | None = None
```

### **Step 2: SQLAlchemy Model**
**파일**: `src/{domain}/infrastructure/database/models/{domain}_model.py`

```python
class UserModel(Base):
    __tablename__ = "user"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
```

### **Step 3: Repository**
**파일**: `src/{domain}/infrastructure/repositories/{domain}_repository.py`

```python
class UserRepository(BaseRepository[CreateUserEntity, UserEntity, UpdateUserEntity]):
    def __init__(self, database: Database) -> None:
        super().__init__(
            database=database,
            model=UserModel,
            create_entity=CreateUserEntity,
            return_entity=UserEntity,
            update_entity=UpdateUserEntity,
        )
```

### **Step 4-9**: Service, UseCase, DTO, Router, Container, Bootstrap

(각 단계는 위의 Layer-by-Layer Guide 참조)

---

## 6. Do's and Don'ts (필수 준수사항)

### ❌ **절대 하지 말아야 할 것**

1. **Base 클래스 수정 금지**
   - `BaseRepository`, `BaseService`, `BaseUseCase`는 모든 도메인이 의존
   - 수정 시 전체 시스템에 영향

2. **상대 경로 import 금지**
   ```python
   # ❌ 금지
   from ...domain.entities.entity import Entity
   
   # ✅ 사용
   from src._core.domain.entities.entity import Entity
   ```

3. **TypeVar 이름/순서 변경 금지**
   ```python
   # ❌ 금지
   CreateDTO = TypeVar("CreateDTO", bound=Entity)
   
   # ✅ 사용
   CreateEntity = TypeVar("CreateEntity", bound=Entity)
   ```

4. **마이그레이션 파일 수동 수정 금지**
   - 항상 `alembic revision --autogenerate` 사용

5. **API_CONFIG의 alias_generator 변경 금지**
   - `to_camel`은 전체 API 응답 형식의 기준

### ✅ **권장 사항**

1. **커스텀 메서드는 하위 클래스에 추가**
   ```python
   class UserRepository(BaseRepository[...]):
       async def select_data_by_email(self, email: str) -> UserEntity:
           ...
   ```

2. **비즈니스 로직은 Service에 추가**
   - Repository는 데이터 액세스만
   - Service는 비즈니스 규칙 구현

3. **여러 Service 조율은 UseCase에 추가**
   - 복잡한 플로우는 UseCase에서 처리

4. **환경별 설정은 `from_env` 패턴 사용**
   ```python
   @classmethod
   def from_env(cls, env: str) -> "Config":
       if env == "prod":
           return cls(...)
       return cls(...)
   ```

5. **도메인별 커스텀 예외 정의**
   ```python
   class UserNotFoundException(BaseCustomException):
       def __init__(self, user_id: int):
           super().__init__(
               status_code=404,
               message=f"User {user_id} not found",
               error_code="USER_NOT_FOUND",
           )
   ```

---

## 📚 Quick Reference

### **기술 스택**
- Python 3.12.9+
- FastAPI 0.115+
- Pydantic 2.10+
- SQLAlchemy 2.0+ (asyncpg)
- dependency-injector
- aiohttp, aioboto3, taskiq
- SQLAdmin, Alembic

### **핵심 원칙**
1. 모든 비즈니스 로직은 `async def`
2. TypeVar 기반 Generic 프로그래밍
3. 절대 경로 import만 사용
4. Context Manager 패턴 (`async with`)
5. DTO ↔ Entity 명확한 변환 (`to_entity`, `from_entity`)
6. 환경별 설정은 `from_env` 패턴

---

**End of Document**
