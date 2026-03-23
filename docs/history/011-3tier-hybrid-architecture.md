# 011. 3-Tier 하이브리드 아키텍처로 전환

- 상태: Accepted
- 날짜: 2026-03-23
- 관련 이슈: #33
- 관련 ADR: 004-dto-entity-responsibility.md (진화), 006-ddd-layered-architecture.md (진화)

## 배경

프로젝트는 4계층 구조(Router → UseCase → Service → Repository)를 사용하고 있었다.
ADR 004에서 Entity를 DTO로 대체한 후, UseCase와 Service 계층이 모두 "데이터를 그대로 넘기는" 위임 역할만 하고 있었다.

```python
# UseCase — Service 위임만
class UserUseCase:
    async def create_data(self, entity: BaseModel) -> UserDTO:
        return await self.user_service.create_data(entity=entity)

# Service — Repository 위임만
class UserService:
    async def create_data(self, entity: BaseModel) -> UserDTO:
        return await self.user_repository.insert_data(entity=entity)
```

8개 CRUD 메서드 x 2계층 = 16개의 passthrough 메서드가 도메인마다 반복되었다.

## 문제

### 1. UseCase가 Service의 복사본

UserUseCase의 7개 메서드 중 6개는 `self.user_service.method()` 호출이 전부였다.
유일한 추가 로직은 `get_datas`의 pagination 처리뿐이었다.

### 2. Service도 Repository의 복사본

UserService의 8개 메서드 전부가 `self.user_repository.method()` 호출만 했다.
BaseService가 이전에 존재했으나, Entity→DTO 리팩토링 과정에서 제거되면서 수동 위임으로 전환되었다.

### 3. Generic 파라미터 과잉

`BaseRepositoryProtocol[CreateDTO, ReturnDTO, UpdateDTO]`에서 CreateDTO와 UpdateDTO는
항상 `BaseModel`로 설정되어 실질적 타입 안전성을 제공하지 못했다.

```python
# 3개 중 2개가 항상 BaseModel — 의미 없음
class UserRepositoryProtocol(BaseRepositoryProtocol[BaseModel, UserDTO, BaseModel]):
    pass
```

## 검토한 대안

### 1. 현행 유지 (4계층)
- UseCase/Service 위임 boilerplate 16개 메서드 수동 유지
- 도메인 추가 시 매번 동일 boilerplate 복사
- 이점: 계층이 명확. 단점: 실질적 가치 없는 코드 반복

### 2. UseCase 완전 제거 (Router → Service → Repository)
- Service에 pagination 로직 흡수
- 단점: 복잡한 비즈니스 로직이 필요해지면 Service가 비대해짐

### 3. 하이브리드 (선택)
- 단순 CRUD: Router → Service → Repository (UseCase 생략)
- 복합 로직: Router → UseCase → Service → Repository (UseCase 유지)
- BaseService 복원으로 Service boilerplate도 제거

## 결정

**3-Tier 하이브리드 아키텍처 채택**

### 변경 1: Generic 간소화 (3개 → 1개)

```python
# Before
BaseRepositoryProtocol[CreateDTO, ReturnDTO, UpdateDTO]  # 3개
BaseRepository[CreateDTO, ReturnDTO, UpdateDTO]

# After
BaseRepositoryProtocol[ReturnDTO]  # 1개 — 의미있는 것만
BaseRepository[ReturnDTO]
```

Write 방향은 Request를 그대로 넘기므로 `BaseModel`을 파라미터 타입으로 직접 사용한다.

### 변경 2: BaseService 복원

```python
class BaseService(Generic[ReturnDTO]):
    def __init__(self, repository: BaseRepositoryProtocol[ReturnDTO]):
        self.repository = repository

    async def create_data(self, entity: BaseModel) -> ReturnDTO: ...
    async def get_datas(self, page, page_size) -> tuple[list[ReturnDTO], PaginationInfo]: ...
    # CRUD 위임 + pagination 자동 제공
```

도메인 Service는 상속만으로 CRUD 완료:

```python
class UserService(BaseService[UserDTO]):
    def __init__(self, user_repository: UserRepositoryProtocol):
        super().__init__(repository=user_repository)
    # 커스텀 메서드만 추가
```

### 변경 3: UseCase 선택적 사용

```
단순 CRUD:  Router → Service(BaseService 상속) → Repository
복합 로직:  Router → UseCase(수동 작성) → Service → Repository
```

UseCase 추가 기준:
- 여러 Service를 조합해야 할 때
- 트랜잭션 경계가 Service 단위를 넘을 때
- 이벤트 발행 등 orchestration이 필요할 때

### 변경 4: 용어 통일

| 용어 | 역할 | 위치 |
|------|------|------|
| Request/Response | API 통신 규격 | `interface/server/dtos/` |
| DTO | 내부 레이어 간 데이터 운반 | `domain/dtos/` |
| Model | DB 테이블 매핑 | `infrastructure/database/models/` |
| Entity | 사용하지 않음 | - |

## 근거

| 기준 | 4계층 (이전) | 3-Tier 하이브리드 (현재) |
|------|------------|----------------------|
| Service boilerplate | 8개 메서드 수동 작성 | BaseService 상속 (0줄) |
| UseCase boilerplate | 7개 메서드 수동 작성 | 필요할 때만 생성 |
| Generic 타입 안전성 | 3개 중 2개 무의미 | 1개 (ReturnDTO)만 의미있게 |
| 도메인 추가 비용 | UseCase + Service 파일 2개 | Service 파일 1개 (5줄) |
| 복합 로직 대응 | UseCase 항상 존재 | UseCase 필요 시 추가 |

1. CRUD 위주 도메인에서 UseCase는 불필요한 위임 레이어 — passthrough 제거로 코드 명확성 향상
2. BaseService가 Spring Boot의 CRUD Service, NestJS의 TypeOrmCrudService와 동일한 패턴
3. UseCase를 선택적으로 유지하여 복합 로직 확장성 보존
4. Generic 간소화로 타입 시그니처가 실제 의미를 반영

## 교훈

- 계층이 많다고 좋은 아키텍처가 아니다. 각 계층이 실질적 가치를 제공하는지 검증해야 한다
- "나중에 필요할 수 있으니 미리 만들어두자"는 YAGNI 위반이다. 필요해지면 그때 추가하면 된다
- Base 클래스를 통한 CRUD 자동화는 엔터프라이즈에서 검증된 패턴이다 (Spring, NestJS, Django)
