# 가이드라인 동기화 점검 항목 상세

## 1. CLAUDE.md ↔ 코드 일치 확인

CLAUDE.md를 읽고 각 섹션을 실제 코드와 대조:

- [ ] **절대 금지 규칙**: 실제로 위반 사례가 없는지 Grep으로 확인
  - `from src.*.infrastructure` in domain/ 파일
  - `to_entity(` 또는 `from_entity(` 호출
  - `class.*Mapper` 정의
  - Response/Request 다중상속 패턴
- [ ] **변환 패턴**: CLAUDE.md에 기술된 4가지 패턴이 실제 코드에서 동일하게 사용되는지
  - Request → Service: `entity=item` 직접 전달
  - Model → DTO: `model_validate(model, from_attributes=True)`
  - DTO → Response: `model_dump(exclude={...})`
- [ ] **Write DTO 기준**: 현재 Request/DTO 사용 방식이 기준과 일치하는지

## 2. Skills ↔ 코드 일치 확인

각 스킬의 SKILL.md를 읽고 레퍼런스 코드와 대조:

- [ ] **`/new-domain`**: 파일 목록이 `src/user/` 실제 구조와 일치하는지
  - 새로 추가된 파일이 Skills에 반영되지 않았는지
  - 삭제된 파일이 Skills에 여전히 남아있는지
  - import 경로가 실제 base class 위치와 일치하는지
  - 클래스 시그니처 (Generic 타입 파라미터 등)가 일치하는지
- [ ] **`/add-api`**: 구현 순서와 패턴이 현재 코드와 일치하는지
  - Router 데코레이터 패턴 (`@inject`, `Depends(Provide[...])`)
  - SuccessResponse 사용 패턴
- [ ] **`/add-worker-task`**: 태스크 패턴이 현재 broker 설정과 일치하는지
  - `@broker.task` 데코레이터 사용법
  - DI wiring 패턴
- [ ] **`/review-architecture`**: 체크항목이 현재 규칙을 모두 포함하는지
- [ ] **`/test-domain`**: 테스트 패턴이 실제 테스트 코드와 일치하는지
- [ ] **`/add-cross-domain`**: Protocol 기반 의존성 패턴이 현재와 일치하는지

## 3. Serena 메모리 ↔ 현재 상태 확인

Serena 메모리를 읽고 현재 코드와 대조:

- [ ] **`architecture_conventions`**: DO/DON'T 규칙이 CLAUDE.md 및 실제 코드와 일치하는지
- [ ] **`refactoring_status`**: 현재 진행 상황이 정확한지
- [ ] **`project_overview`**: 기술 스택, 엔트리 포인트 등이 최신인지
