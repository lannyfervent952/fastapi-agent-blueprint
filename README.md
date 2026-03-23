# FastAPI Blueprint

[![Python](https://img.shields.io/badge/Python-3.12.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

**CRUD 반복을 끝내는 FastAPI 백엔드 청사진.**
Base 클래스 상속 한 줄로 7개 CRUD 자동 제공. 새 도메인은 만들기만 하면 자동 등록.

---

## Why?

```python
# Before: 도메인마다 동일한 CRUD 반복
@router.post("/user")
async def create_user(user: UserCreate):
    db = get_db()
    new_user = User(**user.dict())
    db.add(new_user)
    db.commit()
    return new_user

@router.post("/product")  # 또 반복...
async def create_product(product: ProductCreate):
    db = get_db()
    new_product = Product(**product.dict())
    db.add(new_product)
    db.commit()
    return new_product
```

```python
# After: 베이스 클래스 상속 한 줄로 CRUD 완료
class ProductRepository(BaseRepository[ProductDTO]):
    def __init__(self, database: Database):
        super().__init__(database=database, model=ProductModel, return_entity=ProductDTO)

class ProductService(BaseService[ProductDTO]):
    def __init__(self, product_repository: ProductRepositoryProtocol):
        super().__init__(repository=product_repository)

# 7개 CRUD 메서드 자동 제공 — 커스텀 로직만 추가하면 됨
```

---

## Architecture

```
Router → Service(BaseService) → Repository(BaseRepository) → DB
              ↑ 단순 CRUD는 이것만으로 충분

Router → UseCase → Service → Repository → DB
              ↑ 복잡한 비즈니스 로직이 필요할 때만 추가
```

### 계층별 책임

| 계층 | 역할 | Base 클래스 |
|------|------|------------|
| **Interface** | Router, Request/Response, Admin, Worker Task | - |
| **Domain** | Service (비즈니스 로직), Protocol, DTO, Event | `BaseService[ReturnDTO]` |
| **Infrastructure** | Repository (DB 접근), Model, DI Container | `BaseRepository[ReturnDTO]` |
| **Application** | UseCase (복합 로직 조율) — **선택적** | - |

### 데이터 흐름

```
Write: Request ──→ Service ──→ Repository ──→ Model → DB
Read:  Response ←── Service ←── Repository ←── DTO ←── Model
```

- Request를 Service에 직접 전달 (별도 변환 불필요)
- Repository가 Model → DTO 변환 (`model_validate(model, from_attributes=True)`)
- Router가 DTO → Response 변환 (`Response(**dto.model_dump(exclude={...}))`)

### 데이터 객체

| 객체 | 역할 | 위치 |
|------|------|------|
| **Request/Response** | API 통신 규격 | `interface/server/dtos/` |
| **DTO** | 내부 레이어 간 데이터 운반 | `domain/dtos/` |
| **Model** | DB 테이블 매핑 (Repository 밖으로 노출 금지) | `infrastructure/database/models/` |

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/Mr-DooSun/fastapi-blueprint.git
cd fastapi-blueprint

# 2. 가상환경 + 의존성 설치 (UV 권장)
uv venv --python 3.12
source .venv/bin/activate
uv sync

# 3. 환경변수 설정
cp _env/local.env.example _env/local.env

# 4. PostgreSQL 실행 (Docker)
docker run -d \
  --name postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=postgres \
  -p 5432:5432 \
  postgres:16

# 5. 마이그레이션 + 서버 실행
alembic upgrade head
python run_server_local.py --env local
```

http://localhost:8000/docs-swagger 에서 API 확인

---

## 새 도메인 추가하기

Product 도메인을 예로 들면:

### 1. Domain Layer

```python
# src/product/domain/dtos/product_dto.py
class ProductDTO(BaseModel):
    id: int = Field(..., description="제품 ID")
    name: str = Field(..., description="제품명")
    price: int = Field(..., description="가격")
    created_at: datetime
    updated_at: datetime

# src/product/domain/protocols/product_repository_protocol.py
class ProductRepositoryProtocol(BaseRepositoryProtocol[ProductDTO]):
    pass

# src/product/domain/services/product_service.py
class ProductService(BaseService[ProductDTO]):
    def __init__(self, product_repository: ProductRepositoryProtocol):
        super().__init__(repository=product_repository)
    # CRUD 자동 제공. 커스텀 로직만 추가.
```

### 2. Infrastructure Layer

```python
# src/product/infrastructure/database/models/product_model.py
class ProductModel(Base):
    __tablename__ = "product"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, onupdate=func.now())

# src/product/infrastructure/repositories/product_repository.py
class ProductRepository(BaseRepository[ProductDTO]):
    def __init__(self, database: Database):
        super().__init__(database=database, model=ProductModel, return_entity=ProductDTO)

# src/product/infrastructure/di/product_container.py
class ProductContainer(containers.DeclarativeContainer):
    core_container = providers.DependenciesContainer()
    product_repository = providers.Singleton(ProductRepository, database=core_container.database)
    product_service = providers.Factory(ProductService, product_repository=product_repository)
```

### 3. Interface Layer

```python
# src/product/interface/server/routers/product_router.py
@router.post("/product", response_model=SuccessResponse[ProductResponse])
@inject
async def create_product(
    item: CreateProductRequest,
    product_service: ProductService = Depends(Provide[ProductContainer.product_service]),
) -> SuccessResponse[ProductResponse]:
    data = await product_service.create_data(entity=item)
    return SuccessResponse(data=ProductResponse(**data.model_dump()))
```

### 자동 등록

`discover_domains()`가 새 도메인을 자동 탐지합니다.
`_apps/` 내 container나 bootstrap을 **수정할 필요 없습니다**.

자동 발견 조건:
- `src/{name}/__init__.py` 존재
- `src/{name}/infrastructure/di/{name}_container.py` 존재

---

## Tech Stack

### Core

| 기술 | 용도 |
|------|------|
| **FastAPI** | 비동기 웹 프레임워크 |
| **Pydantic** 2.x | 데이터 검증, Settings |
| **SQLAlchemy** 2.0 | 비동기 ORM |
| **dependency-injector** | IoC Container (DIP 실현) |

### Infrastructure

| 기술 | 용도 |
|------|------|
| **PostgreSQL** + asyncpg | 메인 RDBMS |
| **Taskiq** + AWS SQS | 비동기 태스크 큐 |
| **aiohttp** | 비동기 HTTP 클라이언트 |
| **aioboto3** | S3/MinIO 스토리지 |
| **Alembic** | DB 마이그레이션 |

### DevOps

| 기술 | 용도 |
|------|------|
| **Ruff** | 린팅 + 포맷팅 (6개 도구 통합) |
| **pre-commit** | Git hook 자동화 |
| **UV** | Python 패키지 관리 |
| **SQLAdmin** | DB 관리 UI |

---

## Project Structure

```
src/
├── _apps/                        # App-level 진입점
│   ├── server/                  # API 서버
│   ├── worker/                  # Taskiq 워커
│   └── admin/                   # Admin UI
│
├── _core/                        # 공통 인프라
│   ├── domain/
│   │   ├── protocols/           # BaseRepositoryProtocol[ReturnDTO]
│   │   └── services/            # BaseService[ReturnDTO]
│   ├── infrastructure/
│   │   ├── database/            # Database, BaseRepository[ReturnDTO]
│   │   ├── http/                # HttpClient, BaseHttpGateway
│   │   ├── taskiq/              # SQS Broker, TaskiqManager
│   │   ├── storage/             # S3/MinIO
│   │   ├── di/                  # CoreContainer
│   │   └── discovery.py         # 도메인 자동 발견
│   ├── application/dtos/        # BaseRequest, BaseResponse, SuccessResponse
│   ├── middleware/               # ExceptionMiddleware
│   └── config.py                # Settings (pydantic-settings)
│
├── user/                         # 예시 도메인
│   ├── domain/
│   │   ├── dtos/                # UserDTO
│   │   ├── protocols/           # UserRepositoryProtocol
│   │   ├── services/            # UserService(BaseService[UserDTO])
│   │   ├── exceptions/          # UserNotFoundException
│   │   └── events/              # UserCreated, UserUpdated
│   ├── infrastructure/
│   │   ├── database/models/     # UserModel
│   │   ├── repositories/        # UserRepository(BaseRepository[UserDTO])
│   │   └── di/                  # UserContainer
│   └── interface/
│       ├── server/              # routers/, dtos/, bootstrap/
│       ├── worker/              # tasks/, bootstrap/
│       └── admin/               # SQLAdmin views
│
├── migrations/                   # Alembic
├── _env/                         # 환경변수
└── docs/history/                 # Architecture Decision Records
```

---

## Architecture Decisions

이 프로젝트의 모든 기술 선택은 ADR(Architecture Decision Record)로 기록되어 있습니다.

| # | 제목 |
|---|------|
| [004](docs/history/004-dto-entity-responsibility.md) | DTO/Entity 책임 재정의 |
| [006](docs/history/006-ddd-layered-architecture.md) | 도메인별 레이어드 아키텍처 전환 |
| [007](docs/history/007-di-container-and-app-separation.md) | DI 컨테이너 계층화와 앱 분리 |
| [011](docs/history/011-3tier-hybrid-architecture.md) | 3-Tier 하이브리드 아키텍처 전환 |
| [012](docs/history/012-ruff-migration.md) | Ruff 도입 |
| [013](docs/history/013-why-ioc-container.md) | 상속 대신 IoC Container를 선택한 이유 |

[전체 목록 보기](docs/history/README.md)

---

## AI Pair Programming (AIDD)

이 프로젝트는 **AIDD(AI-Driven Development)** 방법론을 적용하여 Claude Code와 페어 프로그래밍이 가능합니다.

### 내장 Skills

| 명령어 | 기능 |
|--------|------|
| `/new-domain {name}` | 도메인 전체 스캐폴딩 자동 생성 |
| `/add-api {description}` | 기존 도메인에 API 엔드포인트 추가 |
| `/add-worker-task {domain} {task}` | 비동기 Taskiq 태스크 추가 |
| `/add-cross-domain from:{a} to:{b}` | 도메인 간 의존성 연결 |
| `/review-architecture {domain}` | 아키텍처 컴플라이언스 감사 |
| `/security-review {domain}` | OWASP 기반 보안 감사 |
| `/test-domain {domain}` | 테스트 생성/실행 |
| `/fix-bug {description}` | 구조화된 버그 수정 |
| `/plan-feature {description}` | 기능 구현 계획 수립 |
| `/sync-guidelines` | 설계 변경 후 문서 동기화 점검 |

### MCP 서버 설정

AIDD 기능을 사용하려면 다음 MCP 서버가 필요합니다:

**Serena** — 심볼릭 코드 탐색/편집 (LSP 수준의 rename, reference 분석)
```json
{
  "mcpServers": {
    "serena": {
      "command": "uvx",
      "args": ["--from", "serena-mcp", "serena", "--project-root", "."]
    }
  }
}
```

**context7** — 라이브러리 최신 문서 조회
```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"]
    }
  }
}
```

> MCP 서버 없이도 프로젝트 자체는 정상 동작합니다. AIDD 기능(Skills)을 활용하려면 설정이 필요합니다.

---

## Contributing

```bash
# pre-commit 설치
pre-commit install

# 코드 검사
ruff check src/ --fix
ruff format src/
```

### Commit Convention

```
feat: 새로운 기능
fix: 버그 수정
refactor: 리팩토링
docs: 문서 수정
chore: 빌드/도구 변경
test: 테스트
```

---

## License

[MIT License](LICENSE) — 상업적 사용, 수정, 배포 자유.
