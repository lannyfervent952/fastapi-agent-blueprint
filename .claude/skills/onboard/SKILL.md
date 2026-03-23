---
name: onboard
argument-hint: "(no arguments)"
description: |
  This skill should be used when the user asks to "온보딩",
  "프로젝트 소개", "project introduction", "시작하기",
  "getting started", "how does this project work",
  "아키텍처 설명해줘", "구조 알려줘", "처음 왔어요",
  "I'm new to this project", "프로젝트 구조",
  or is a new team member needing orientation to the project.
---

# 신규 인력 대화형 온보딩

> **설계 원칙**: 이 스킬은 자체 아키텍처 문서를 갖지 않는다.
> 모든 정보는 기존 소스(README.md, ADR, project-dna.md, CLAUDE.md, Serena 메모리, src/user/ 코드)를
> 런타임에 읽어서 제공한다. 구조가 바뀌면 원본이 갱신되고, 온보딩은 자동으로 최신 내용을 반영한다.

## Pre-check: 프로젝트 상태 수집

아래를 실행하여 현재 프로젝트 상태를 파악한다 (사용자에게 출력하지 않는다):

1. Serena `project_overview` 메모리 읽기 — 기술 스택 및 앱 구조
2. Serena `refactoring_status` 메모리 읽기 — 진행 중인 작업 확인
3. Serena `architecture_conventions` 메모리 읽기 — 현재 DO/DON'T 규칙
4. Glob `src/*/` 으로 현재 도메인 목록 파악 (`_core`, `_apps` 제외)
5. `git log --oneline -5` 로 최근 활동 파악

## Phase 0: Welcome — 경험 수준 파악

사용자에게 경험 수준을 질문한다:

> 환영합니다! 온보딩을 시작하기 전에 한 가지 질문드립니다.
>
> **Python/FastAPI 경험은 어느 정도인가요?**
> - **(1) 입문** — Python 기초, FastAPI 처음
> - **(2) 중급** — FastAPI 경험 있음, DDD/레이어드 아키텍처 처음
> - **(3) 고급** — DDD + DI Container 경험 있음, 이 프로젝트 구조만 파악 필요

사용자 응답을 받은 후, `${CLAUDE_SKILL_DIR}/references/role-tracks.md`의 레벨별 조정 기준을 참조하여
각 Phase의 깊이를 조정한다. 트랙 안내:

```
=== 온보딩 트랙 ===
경험: {선택된 레벨}
Phase: 1(방법론) → 2(프로젝트 개요) → 3(아키텍처 규칙) → 4(데이터 흐름) → 5(Skills) → 6(다음 단계)
깊이 조정: {레벨에 따른 조정 요약}
```

사용자 확인 후 다음 Phase로 진행한다.

## Phase 1: 방법론과 아키텍처 진화 히스토리

**정보 소스**: `README.md`, `docs/history/` ADR 파일들

> 이 Phase는 "왜 이렇게 만들어졌는지"를 이해시키는 것이 목적이다.
> 규칙과 구조를 설명하기 전에, 그 배경을 먼저 전달해야 규칙이 와닿는다.

### 1.1 DDD (Domain-Driven Design) 핵심 개념

다음을 설명한다:
- **Bounded Context**: 도메인마다 독립적인 모델과 로직을 갖는다. 이 프로젝트에서는 `src/{domain}/`이 하나의 Bounded Context
- **레이어드 아키텍처**: 관심사를 분리하여 각 레이어가 독립적으로 교체/테스트 가능하게 만든다
- **의존성 방향**: Interface → Application → Domain ← Infrastructure (Domain이 중심, Infrastructure를 모름)

**경험 레벨 조정**:
- **입문**: 각 개념을 비유를 들어 상세 설명. "레이어는 건물의 층과 같아서, 위층(Router)은 아래층(Service)을 알지만 아래층은 위층을 모릅니다"
- **중급**: 개념만 간단히 짚고 넘어감
- **고급**: DDD 개념 설명 스킵, 바로 1.2로

### 1.2 이 프로젝트의 진화 과정

`docs/history/` 디렉토리의 ADR을 참조하여, 주요 결정이 어떤 **문제**에서 출발했는지를 이야기 형식으로 전달한다:

**스토리 1: 구조의 진화**
- `docs/history/006-ddd-layered-architecture.md`를 읽어 핵심을 전달한다
- "처음에는 apps/와 domains/가 분리되어 있었는데, 코드 탐색이 불편해서 도메인별 평탄화로 전환했다"
- 요점: 도메인 폴더 하나만 열면 해당 기능의 모든 코드를 볼 수 있다

**스토리 2: Entity → DTO 통일**
- `docs/history/004-dto-entity-responsibility.md`를 읽어 핵심을 전달한다
- "Entity를 DDD 패턴대로 도입했지만, 비즈니스 로직이 없어서 DTO와 역할이 중복되었다"
- "to_entity/from_entity 변환이 모든 핸들러에서 반복 → 제거하고 DTO로 통일"
- 요점: 이것이 "Entity 패턴 미사용, DTO 통일" 규칙의 배경

**스토리 3: 4-Tier → 3-Tier 하이브리드**
- `docs/history/011-3tier-hybrid-architecture.md`를 읽어 핵심을 전달한다
- "UseCase → Service → Repository 각각이 아래 계층을 단순 위임만 하고 있었다 (passthrough)"
- "BaseService를 복원하고, UseCase는 필요할 때만 추가하는 하이브리드로 전환"
- 요점: 이것이 "UseCase 선택적" 규칙의 배경. 계층이 많다고 좋은 아키텍처가 아니다

**스토리 4: 왜 IoC Container인가**
- `docs/history/013-why-ioc-container.md`를 읽어 핵심을 전달한다
- "상속은 is-a 관계인데, Service는 Repository가 아니라 사용(has-a)하는 것이다"
- "FastAPI Depends()는 Router에서만 동작 → Worker에서 재사용 불가"
- "Container가 Protocol(인터페이스)과 구현체를 런타임에 연결한다"
- 요점: 이것이 "Domain에서 Infrastructure import 금지" 규칙을 가능하게 하는 메커니즘

### 1.3 AIDD (AI-Driven Development)

`README.md`의 **AI Pair Programming (AIDD)** 섹션을 읽어 다음을 설명한다:
- 이 프로젝트는 Claude Code와 페어 프로그래밍이 가능하도록 설계되었다
- 11개 Skills(slash commands)로 도메인 생성, API 추가, 아키텍처 검증 등을 자동화
- MCP 서버(Serena, context7)로 심볼릭 코드 탐색과 라이브러리 문서 조회 지원
- Skills가 project-dna.md와 CLAUDE.md를 참조하여 프로젝트 규칙을 자동으로 따른다

> "궁금한 점이 있으면 질문해주세요. 없으면 '다음'이라고 해주세요."

## Phase 2: 프로젝트 개요

**정보 소스**: `project-dna.md §0~1`, Serena `project_overview` 메모리

1. `.claude/skills/_shared/project-dna.md`의 **§0 프로젝트 스케일** 섹션을 읽어
   프로젝트의 목적과 규모를 설명한다.

2. 아키텍처 핵심을 다이어그램으로 보여준다 (Phase 1에서 맥락을 이미 알고 있으므로 간결하게):
   ```
   기본: Router → Service(BaseService) → Repository(BaseRepository)
   복합: Router → UseCase → Service → Repository (여러 Service 조합 시)
   ```

3. `project-dna.md`의 **§1 도메인 디렉토리 구조**를 읽어 한 도메인의 파일 구성을 보여준다.

4. Pre-check에서 수집한 현재 도메인 목록과 최근 git 활동을 보여준다.

5. Serena `project_overview` 메모리에서 읽은 기술 스택을 안내한다.

**경험 레벨 조정** (`role-tracks.md` §2 참조):
- **입문**: DI Container, Protocol, Pydantic BaseModel 추가 설명
- **고급**: 도메인 목록 + 기술 스택만 요약 제시

> "궁금한 점이 있으면 질문해주세요. 없으면 '다음'이라고 해주세요."

## Phase 3: 아키텍처 규칙

**정보 소스**: `CLAUDE.md` 절대 금지 섹션

1. `CLAUDE.md`의 **절대 금지 규칙** 섹션을 읽어 4개 규칙을 제시한다.
   Phase 1에서 히스토리를 이미 전달했으므로, 각 규칙이 **어떤 스토리에서 비롯되었는지** 연결해준다:
   - "Domain에서 Infrastructure import 금지" ← 스토리 4 (IoC Container가 이를 가능하게 함)
   - "Model 외부 노출 금지" ← 스토리 2 (DTO가 레이어 간 데이터 전달 담당)
   - "Mapper 클래스 금지" ← 인라인 변환으로 충분 (스토리 2)
   - "Entity 패턴 미사용, DTO 통일" ← 스토리 2 (ADR 004)

2. `CLAUDE.md`의 **용어 정의** 섹션을 읽어 Request/Response, DTO, Model의 역할과 위치를 설명한다.

**경험 레벨 조정**:
- **고급**: 규칙 목록 + 스토리 연결만 간결하게

> "궁금한 점이 있으면 질문해주세요. 없으면 '다음'이라고 해주세요."

## Phase 4: 데이터 흐름 워크스루

**정보 소스**: `CLAUDE.md` 변환 패턴 섹션, `src/user/` 라이브 코드

1. `CLAUDE.md`의 **변환 패턴** 섹션(Write 방향, Read 방향)을 읽어 전체 흐름을 보여준다.

2. `src/user/` 도메인의 실제 코드를 라이브로 읽어 구체적인 예시를 보여준다:

   **Write 경로 (생성):**
   - Serena `find_symbol`로 Request DTO를 읽어 필드 구조를 보여준다
   - Router의 create 메서드를 읽어 Request → Service 전달 패턴을 보여준다
   - Repository의 insert 메서드를 읽어 `Model(**entity.model_dump())` 변환을 보여준다

   **Read 경로 (조회):**
   - Repository의 select 메서드를 읽어 `DTO.model_validate(model)` 변환을 보여준다
   - Router의 response 반환 패턴을 보여준다

**경험 레벨 조정**:
- **고급**: 변환 패턴 요약 테이블만 제시, 코드 워크스루 생략

> "궁금한 점이 있으면 질문해주세요. 없으면 '다음'이라고 해주세요."

## Phase 5: 개발 워크플로우 및 Skills

**정보 소스**: `CLAUDE.md` Skills 섹션, Serena `suggested_commands` 메모리

1. `CLAUDE.md`의 **작업별 Skills** 섹션을 읽어 전체 Skills 목록을 워크플로우 순서로 안내한다:
   > "새 기능을 개발할 때 이 순서로 Skills를 사용합니다:"
   > 설계(`/plan-feature`) → 생성(`/new-domain`, `/add-api`) → 검증(`/review-architecture`, `/test-domain`) → 수정(`/fix-bug`)

2. Serena `suggested_commands` 메모리를 읽어 자주 사용하는 명령어(서버 실행, 테스트, lint 등)를 안내한다.

**경험 레벨 조정**:
- **고급**: Skills 목록만 제시

> "궁금한 점이 있으면 질문해주세요. 없으면 '다음'이라고 해주세요."

## Phase 6: 맞춤 다음 단계

**정보 소스**: `role-tracks.md` §4 다음 단계 추천

`${CLAUDE_SKILL_DIR}/references/role-tracks.md` §4에서 사용자의 경험 레벨에 해당하는
"첫 3개 태스크"를 읽어 제시한다.

마무리:
```
=== 온보딩 완료 ===
추가 질문이 있으면 언제든 물어보세요.

핵심 참고 자료:
- CLAUDE.md — 프로젝트 규칙 전체
- .claude/skills/_shared/project-dna.md — 코드 패턴 레퍼런스
- docs/history/ — 아키텍처 결정 기록 (ADR)
- src/user/ — 레퍼런스 도메인 구현
```
