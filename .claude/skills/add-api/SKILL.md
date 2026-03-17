---
name: add-api
description: |
  This skill should be used when the user asks to "API 추가",
  "엔드포인트 추가", "add endpoint", "라우터 추가",
  or wants to add a new route to an existing domain.
---

# API 엔드포인트 추가

요청: $ARGUMENTS

## 분석

1. 요청에서 파악: 도메인명, HTTP 메서드, 경로, 목적
2. Serena `find_symbol`로 해당 도메인의 기존 Router, UseCase, Service, Repository 탐색
3. 필요한 것 판단:
   - 새 Request/Response DTO가 필요한가? (기존 것으로 충분한가?)
   - 새 Service 메서드가 필요한가? (BaseRepository 메서드로 충분한가?)
   - 새 UseCase 메서드가 필요한가?
   - 새 Repository 메서드가 필요한가? (커스텀 쿼리가 필요한가?)

## 구현 순서 (Bottom-up)

### 1. Repository (커스텀 쿼리가 필요한 경우만)
- Protocol에 메서드 시그니처 추가: `src/{name}/domain/protocols/{name}_repository_protocol.py`
- Repository에 구현 추가: `src/{name}/infrastructure/repositories/{name}_repository.py`
- BaseRepository 메서드로 충분하면 이 단계 생략

### 2. Service
- `src/{name}/domain/services/{name}_service.py`에 메서드 추가
- Repository 메서드를 호출하는 위임 패턴 유지

### 3. UseCase
- `src/{name}/application/use_cases/{name}_use_case.py`에 메서드 추가
- 목록 조회면 `make_pagination()` 적용
- 비즈니스 로직이 있으면 여기에 추가

### 4. Interface DTO (필요한 경우)
- `src/{name}/interface/server/dtos/{name}_dto.py`에 Request/Response 추가
- Request는 `BaseRequest` 상속, Response는 `BaseResponse` 상속
- **다중상속 금지**

### 5. Router
- `src/{name}/interface/server/routers/{name}_router.py`에 엔드포인트 추가
- 패턴:
  ```python
  @router.{method}("/{path}", summary="설명", response_model=SuccessResponse[{Name}Response])
  @inject
  async def endpoint_name(
      ...,
      {name}_use_case: {Name}UseCase = Depends(Provide[{Name}Container.{name}_use_case]),
  ) -> SuccessResponse[{Name}Response]:
      data = await {name}_use_case.method(...)
      return SuccessResponse(data={Name}Response(**data.model_dump(exclude={...})))
  ```

## 변환 규칙 (CLAUDE.md)
- Request → Service: `entity=item` 직접 전달 (필드 동일 시)
- Request → 별도 DTO: `CreateNameDTO(**item.model_dump(), extra_field=...)` (필드 다를 시)
- DTO → Response: `{Name}Response(**data.model_dump(exclude={...}))` (인라인)

## 완료 후 검증
1. pre-commit 실행
2. 해당 도메인 단위 테스트에 새 메서드 테스트 추가
3. 서버 실행 후 Swagger에서 엔드포인트 확인 가능 안내
