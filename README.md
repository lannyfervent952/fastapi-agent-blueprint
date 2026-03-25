# FastAPI Blueprint

[![Python](https://img.shields.io/badge/Python-3.12.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

**Production-ready FastAPI backend blueprint.** Inherit one base class, get 7 CRUD endpoints. Add a domain, it registers itself.

Designed for teams of 5+ developers managing 10+ domains.

[**Quick Start**](#quick-start) | [**Add a Domain**](#adding-a-new-domain) | [**Architecture**](#architecture) | [:kr: **한국어**](docs/README.ko.md)

---

## Key Features

- **Zero-boilerplate CRUD** -- Inherit `BaseRepository[DTO]` + `BaseService[DTO]`, get 7 async CRUD methods instantly
- **Auto domain discovery** -- Add a domain folder, it auto-registers. No container or bootstrap changes needed
- **4 interface types** -- HTTP API (FastAPI) + Async Worker (Taskiq) + Admin UI (SQLAdmin) + MCP Server (planned)
- **Architecture enforcement** -- Pre-commit hooks block `Domain -> Infrastructure` imports at commit time
- **Type-safe generics** -- `BaseRepository[ProductDTO]`, `BaseService[ProductDTO]`, `SuccessResponse[ProductResponse]`
- **DDD layered structure** -- Each domain is fully independent with its own layers (Domain / Infrastructure / Interface / Application)
- **12 AI development skills** -- Claude Code slash commands for scaffolding, testing, architecture review, and more
- **14 Architecture Decision Records** -- Every major design choice documented with rationale

---

## Why?

```python
# Before: Repeat the same CRUD for every domain
@router.post("/user")
async def create_user(user: UserCreate):
    db = get_db()
    new_user = User(**user.dict())
    db.add(new_user)
    db.commit()
    return new_user

@router.post("/product")  # Repeat again...
async def create_product(product: ProductCreate):
    db = get_db()
    new_product = Product(**product.dict())
    db.add(new_product)
    db.commit()
    return new_product
```

```python
# After: One inheritance line, CRUD done
class ProductRepository(BaseRepository[ProductDTO]):
    def __init__(self, database: Database):
        super().__init__(database=database, model=ProductModel, return_entity=ProductDTO)

class ProductService(BaseService[ProductDTO]):
    def __init__(self, product_repository: ProductRepositoryProtocol):
        super().__init__(repository=product_repository)

# 7 CRUD methods provided automatically -- just add your custom logic
```

---

## Architecture

```
Router -> Service(BaseService) -> Repository(BaseRepository) -> DB
               ^ Simple CRUD: this is all you need

Router -> UseCase -> Service -> Repository -> DB
               ^ Add only when complex business logic is required
```

### Layer Responsibilities

| Layer | Role | Base Class |
|-------|------|-----------|
| **Interface** | Router, Request/Response, Admin, Worker Task | - |
| **Domain** | Service (business logic), Protocol, DTO, Event | `BaseService[ReturnDTO]` |
| **Infrastructure** | Repository (DB access), Model, DI Container | `BaseRepository[ReturnDTO]` |
| **Application** | UseCase (orchestration) -- **optional** | - |

### Data Flow

```
Write: Request --> Service --> Repository --> Model -> DB
Read:  Response <-- Service <-- Repository <-- DTO <-- Model
```

- Request is passed directly to Service (no extra conversion needed)
- Repository handles Model -> DTO conversion (`model_validate(model, from_attributes=True)`)
- Router handles DTO -> Response conversion (`Response(**dto.model_dump(exclude={...}))`)

### Data Objects

| Object | Role | Location |
|--------|------|----------|
| **Request/Response** | API contract | `interface/server/dtos/` |
| **DTO** | Internal data transfer between layers | `domain/dtos/` |
| **Model** | DB table mapping (never exposed outside Repository) | `infrastructure/database/models/` |

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/Mr-DooSun/fastapi-blueprint.git
cd fastapi-blueprint

# 2. Create virtual environment + install dependencies (UV recommended)
uv venv --python 3.12
source .venv/bin/activate
uv sync

# 3. Set up environment variables
cp _env/local.env.example _env/local.env

# 4. Start PostgreSQL (Docker)
docker run -d \
  --name postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=postgres \
  -p 5432:5432 \
  postgres:16

# 5. Run migrations + start server
alembic upgrade head
python run_server_local.py --env local
```

Open http://localhost:8000/docs-swagger to explore the API.

---

## Adding a New Domain

Using `Product` domain as an example:

### 1. Domain Layer

```python
# src/product/domain/dtos/product_dto.py
class ProductDTO(BaseModel):
    id: int = Field(..., description="Product ID")
    name: str = Field(..., description="Product name")
    price: int = Field(..., description="Price")
    created_at: datetime
    updated_at: datetime

# src/product/domain/protocols/product_repository_protocol.py
class ProductRepositoryProtocol(BaseRepositoryProtocol[ProductDTO]):
    pass

# src/product/domain/services/product_service.py
class ProductService(BaseService[ProductDTO]):
    def __init__(self, product_repository: ProductRepositoryProtocol):
        super().__init__(repository=product_repository)
    # CRUD provided automatically. Just add custom logic.
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

### Auto Registration

`discover_domains()` automatically detects new domains.
**No changes needed** in `_apps/` containers or bootstrap files.

Discovery conditions:
- `src/{name}/__init__.py` exists
- `src/{name}/infrastructure/di/{name}_container.py` exists

---

## 4 Interface Types

Each domain can expose functionality through multiple interfaces:

| Interface | Technology | Location | Purpose |
|-----------|-----------|----------|---------|
| **HTTP API** | FastAPI | `interface/server/` | REST API endpoints |
| **Async Worker** | Taskiq + SQS | `interface/worker/` | Background task processing |
| **Admin UI** | SQLAdmin | `interface/admin/` | Database management dashboard |
| **MCP Server** | FastMCP | `interface/mcp/` | AI tool integration (planned) |

All interfaces share the same Domain and Infrastructure layers -- write your business logic once, expose it everywhere.

---

## Tech Stack

### Core

| Technology | Purpose |
|-----------|---------|
| **FastAPI** | Async web framework |
| **Pydantic** 2.x | Data validation & settings |
| **SQLAlchemy** 2.0 | Async ORM |
| **dependency-injector** | IoC Container (DIP) |

### Infrastructure

| Technology | Purpose |
|-----------|---------|
| **PostgreSQL** + asyncpg | Primary RDBMS |
| **Taskiq** + AWS SQS | Async task queue |
| **aiohttp** | Async HTTP client |
| **aioboto3** | S3/MinIO storage |
| **Alembic** | DB migrations |

### DevOps

| Technology | Purpose |
|-----------|---------|
| **Ruff** | Linting + formatting (replaces 6 tools) |
| **pre-commit** | Git hook automation |
| **UV** | Python package management |
| **SQLAdmin** | DB admin UI |

---

## Project Structure

```
src/
├── _apps/                        # App entry points
│   ├── server/                  # FastAPI HTTP server
│   ├── worker/                  # Taskiq async worker
│   └── admin/                   # SQLAdmin dashboard
│
├── _core/                        # Shared infrastructure
│   ├── domain/
│   │   ├── protocols/           # BaseRepositoryProtocol[ReturnDTO]
│   │   └── services/            # BaseService[ReturnDTO]
│   ├── infrastructure/
│   │   ├── database/            # Database, BaseRepository[ReturnDTO]
│   │   ├── http/                # HttpClient, BaseHttpGateway
│   │   ├── taskiq/              # SQS Broker, TaskiqManager
│   │   ├── storage/             # S3/MinIO
│   │   ├── di/                  # CoreContainer
│   │   └── discovery.py         # Auto domain discovery
│   ├── application/dtos/        # BaseRequest, BaseResponse, SuccessResponse
│   ├── middleware/               # ExceptionMiddleware
│   └── config.py                # Settings (pydantic-settings)
│
├── user/                         # Example domain
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
├── _env/                         # Environment variables
└── docs/history/                 # Architecture Decision Records
```

---

## Comparison

| Feature | FastAPI Blueprint | Typical Templates |
|---------|:-:|:-:|
| Auto domain discovery | Yes | No |
| Generic CRUD base classes (7 methods) | Yes | Manual |
| Multi-interface (API + Worker + Admin + MCP) | 4 types | API only |
| Architecture enforcement (pre-commit) | Yes | No |
| AI development skills (Claude Code) | 12 skills | 0 |
| Architecture Decision Records | 14 ADRs | Rare |
| Type-safe generics across all layers | Yes | Partial |
| DI with IoC Container (DIP) | Yes | Varies |

---

## Architecture Decisions

Every technical choice in this project is documented as an ADR (Architecture Decision Record).

| # | Title |
|---|-------|
| [004](docs/history/004-dto-entity-responsibility.md) | DTO/Entity responsibility redefined |
| [006](docs/history/006-ddd-layered-architecture.md) | Domain-driven layered architecture |
| [007](docs/history/007-di-container-and-app-separation.md) | DI container hierarchy and app separation |
| [011](docs/history/011-3tier-hybrid-architecture.md) | 3-Tier hybrid architecture |
| [012](docs/history/012-ruff-migration.md) | Ruff adoption |
| [013](docs/history/013-why-ioc-container.md) | Why IoC Container over inheritance |

[View all ADRs](docs/history/README.md)

---

## AI Pair Programming (AIDD)

This project supports **AIDD (AI-Driven Development)** methodology with Claude Code pair programming.

### Built-in Skills

| Command | Description |
|---------|------------|
| `/new-domain {name}` | Scaffold an entire domain (21+ source files) |
| `/add-api {description}` | Add API endpoint to existing domain |
| `/add-worker-task {domain} {task}` | Add async Taskiq task |
| `/add-cross-domain from:{a} to:{b}` | Wire cross-domain dependency |
| `/review-architecture {domain}` | Architecture compliance audit |
| `/security-review {domain}` | OWASP-based security audit |
| `/test-domain {domain}` | Generate or run tests |
| `/fix-bug {description}` | Structured bug fixing workflow |
| `/plan-feature {description}` | Feature implementation planning |
| `/sync-guidelines` | Sync guidelines after design changes |

### MCP Server Setup

To use AIDD features, configure these MCP servers:

**Serena** -- Symbolic code navigation/editing (LSP-level rename, reference analysis)
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

**context7** -- Up-to-date library documentation
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

> The project works without MCP servers. AIDD features (Skills) require MCP server configuration.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, coding guidelines, and PR process.

---

## License

[MIT License](LICENSE) -- Free for commercial use, modification, and distribution.
