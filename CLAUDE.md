# FastAPI Layered Architecture - Claude 작업 가이드

## 작업 전 필수 확인
1. Serena `refactoring_status` 메모리로 현재 Phase 확인
2. Serena `architecture_conventions` 메모리로 DO/DON'T 확인

## 절대 금지 규칙
- Domain 레이어에서 Infrastructure import 금지
- 다중상속 패턴 금지: `class Response(BaseResponse, Entity)`
- `to_entity()`, `from_entity()` 메서드 사용 금지
- Model 객체를 Repository 밖으로 노출 금지
- Mapper 클래스 별도 생성 금지 (인라인 변환으로 충분)

## 변환 패턴
- Request → Service: `item` 직접 전달 (필드가 동일한 경우)
- Request → 별도 DTO: `CreateNameDTO(**item.model_dump(), extra_field=...)` (필드가 다른 경우)
- Model → DTO: `UserDTO.model_validate(model, from_attributes=True)`
- DTO → Response: `UserResponse(**dto.model_dump(exclude={'password'}))`

## Write DTO 생성 기준
- Request 필드와 동일한 경우: Request를 직접 레이어 DTO로 사용, 별도 Create/Update DTO 불필요
- 필드가 다른 경우 (auth context 주입, 파생 필드 등): `application/` 또는 `domain/dtos/`에 별도 DTO 생성

## 작업별 Skills (slash commands)
- `/new-domain {name}` — 도메인 전체 스캐폴딩 (28개 파일 + 테스트)
- `/add-api {description}` — 기존 도메인에 API 엔드포인트 추가
- `/add-worker-task {domain} {task}` — 비동기 Taskiq 태스크 추가
- `/add-cross-domain from:{a} to:{b}` — 도메인 간 의존성 연결
- `/review-architecture {domain|all}` — 아키텍처 컴플라이언스 감사
- `/test-domain {domain} [generate|run]` — 테스트 생성 또는 실행
- `/fix-bug {description}` — 구조화된 버그 수정 워크플로우
- `/sync-guidelines` — 설계 변경 후 가이드라인 동기화 점검

## MCP 사용 지침
- 코드 탐색: Serena 도구 우선 (`find_symbol`, `find_referencing_symbols`, `get_symbols_overview`)
- 파일 전체 읽기: 심볼 탐색으로 충분하지 않을 때만
- 라이브러리 문법: context7으로 최신 문서 확인 (SQLAlchemy 2.0, Pydantic 2.x, Taskiq 등)
