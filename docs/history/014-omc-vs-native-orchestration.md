# 014. OMC vs 네이티브 오케스트레이션 의사결정

- 상태: Pending
- 날짜: 2026-03-24
- 관련 문서: 없음

## 배경

프로젝트에 11개 도메인 스킬 + Serena + settings.json hooks가 구축되어 있으나,
**오케스트레이션 레이어**(멀티 에이전트 조율, 자율 실행, 모델 라우팅)는 부재한 상태다.

이 빈자리를 채우는 두 가지 선택지가 있다:
1. **OMC(Oh My ClaudeCode)** 도입 — 서드파티 오케스트레이션 래퍼
2. **네이티브** — Claude Code 내장 Plugin 시스템 + `/team` 활용

## 문제

오케스트레이션 레이어 없이 현재 운영 가능하지만, 다음 상황에서 한계가 예상된다:
- 3개 이상 도메인의 동시 리팩토링
- 복합 작업의 자동 분해 및 병렬 실행
- 실서비스 프로젝트로의 이식 시 표준 인터페이스 필요성

## 검토한 대안

### A안: OMC 얇게 도입

오케스트레이션만 OMC에 위임하고, 도메인 스킬은 기존 것을 유지한다.

**장점:**
- `/autopilot`, `/team`, `/ultrapilot` 즉시 사용 (zero-config)
- 28개 사전 정의 에이전트 (executor, debugger, designer 등)
- 모델 티어 자동 라우팅 (Haiku/Sonnet/Opus)
- 멀티 프로바이더 (`omc ask codex/gemini`)
- 커뮤니티 표준 인터페이스 → 프로젝트 간 이동 시 러닝커브 감소

**단점:**
- 외부 npm 의존성 (`npm install -g oh-my-claudecode`)
- OMC의 자율 에이전트가 아키텍처 절대 금지 규칙을 위반할 리스크
- 28개 에이전트 정의의 컨텍스트 윈도우 오버헤드
- OMC 메인테이너 의존성 (Claude Code 업데이트 시 호환성 리스크)
- Learner(스킬 자동 제안)로 인한 스킬 누적 + 키워드 충돌 리스크

### B안: 네이티브 Plugin 시스템 + /team

Claude Code 공식 Plugin 시스템으로 commands/agents/hooks를 구축한다.

**장점:**
- Anthropic 공식 — 장기 안정성 보장
- 외부 의존성 없음 (디렉토리 드롭인)
- 기존 11개 스킬이 그대로 호환
- 컨텍스트 오버헤드 최소화 (필요한 것만 정의)
- `/team` 명령어가 이미 내장 (멀티 에이전트 조율)

**단점:**
- autopilot, 모델 티어링 등을 직접 구현해야 함
- 커뮤니티 표준이 아님 → 프로젝트마다 구조가 다를 수 있음
- 초기 구축 비용이 OMC보다 높음

### C안: OMC 전면 도입

기존 스킬을 OMC 포맷으로 마이그레이션하고 Conductor 모델을 전면 적용한다.

**단점이 A안보다 커서 조기 탈락:**
- 기존 11개 스킬 마이그레이션 비용
- OMC에 대한 완전한 의존
- 팀 OMC 숙련도가 0인 상태에서 전면 도입은 리스크가 큼

## 1차 논의 (cross-session-briefing 세션)

**결론: B안 선택**

당시 전제:
- 11개 스킬 + Serena + hooks가 OMC 기능을 이미 더 정밀하게 커버
- 팀 OMC 숙련도 0, 보수적 팀 문화
- 멀티 에이전트가 필요한 작업이 현재 없음

러닝커브 분석:

| 배워야 하는 것 | 비중 | OMC가 해결? |
|---|---|---|
| DDD 4계층 규칙, 절대 금지 사항 | 30% | X |
| 변환 패턴 (model_validate, model_dump) | 15% | X |
| 도메인 고유 지식 | 25% | X |
| 스킬의 내용 (각 스킬이 뭘 하는지) | 20% | X |
| 스킬의 호출 방법 | 5% | O |
| 오케스트레이션 사용법 | 5% | O |

OMC가 줄여주는 러닝커브는 ~10%뿐이고, 핵심 90%는 `/onboarding` 스킬로 해결.

합의된 에스컬레이션 경로:
```
단일 에이전트 → Agent Teams → (필요 시) OMC
```

## 2차 논의 (2026-03-24, 이번 세션)

### 재검토 배경

1차 논의의 전제가 달라짐:
- hooks가 **아직 미구성**, Agent Teams도 **미구성**
- 오케스트레이션 레이어가 실제로 **비어있는 상태**
- 이 상태에서 직접 구축하는 것과 OMC를 얹는 것의 비용 비교 필요

### context7 조사 결과 (신규 발견)

**Claude Code 네이티브 Plugin 시스템 확인:**

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json          # 메타데이터
├── commands/                 # 슬래시 커맨드 (*.md)
├── agents/                   # 특화된 에이전트 (*.md)
├── skills/                   # 스킬 (SKILL.md)
├── hooks/                    # 이벤트 핸들러 (hooks.json)
├── .mcp.json                 # MCP 도구 설정
└── README.md
```

- Claude Code에 `/team` 명령어가 **이미 내장** (native team agents with built-in coordination)
- Plugin 시스템이 OMC와 **동일한 구조** (commands/agents/skills/hooks)
- OMC 문서에서 직접 언급: "native '/team' utilizes Claude Code native team agents"

**OMC의 실제 차별점 (축소됨):**

| 기능 | Claude Code 내장 | OMC 추가분 |
|---|---|---|
| 멀티 에이전트 | `/team` (내장) | `/omc-teams` (tmux 외부 워커) |
| 스킬 시스템 | SKILL.md (내장) | 동일 포맷 |
| 에이전트 정의 | `agents/*.md` (Plugin) | 28개 사전 정의 |
| 자율 실행 | 커스텀 command 작성 | `/autopilot`, `/ultrapilot` 즉시 사용 |
| 모델 라우팅 | 수동 지정 | 자동 티어링 |
| 멀티 프로바이더 | X | `omc ask codex/gemini` |

**벤치마크 점수:**
- Claude Code Plugin: 80.85
- OMC: 75.44
- Claude Code Tresor (대안 플러그인 팩): 78.65

### 핵심 인사이트

1. **도메인 특화는 Skills가 담당** — OMC든 네이티브든 도메인 스킬은 동일하게 직접 작성해야 함
2. **OMC의 추가 가치는 오케스트레이션 편의성** — autopilot, 모델 티어링, 28 에이전트
3. **Claude Code Plugin이 OMC와 동일 방향으로 수렴 중** — Anthropic 공식 지원
4. **내장 `/team` + Plugin을 아직 써보지 않은 상태** — OMC 도입 전에 내장 기능 평가가 먼저
5. **스킬 포맷이 호환** — 네이티브로 시작해도 나중에 OMC 전환 비용 낮음

### OMC 도입 찬성 논거 (2차 논의에서 추가)

- 내장 기능을 직접 구축하는 것보다 OMC가 편리한 것은 사실
- OMC를 아는 사람이 프로젝트에 오면 오케스트레이션은 즉시 사용 가능
- 커뮤니티 표준으로 수렴 중 → 프로젝트 간 이동 자유도

### 네이티브 선택 명분 (2차 논의에서 정리)

- "내장 기능을 써보지도 않고 외부 도구를 도입하는 것은 평가 없는 의사결정"
- Anthropic 공식 Plugin 시스템이 같은 방향으로 수렴 → 장기적으로 더 안정적
- OMC는 언제든 나중에 추가 가능하지만, 도입 후 제거는 어려움
- 컨텍스트 윈도우 절약 (28개 에이전트 정의 미로드)

## 현재 결정

**Pending — 미결정**

에스컬레이션 경로는 유지:
```
단일 에이전트 (현재)
  → /team(내장) + Plugin 시스템 평가
  → 부족 시: OMC 도입
  → 트리거: 3개 이상 도메인 동시 작업에서 내장 기능의 한계 확인
```

## 다음 단계

1. Claude Code 내장 `/team` + Plugin 시스템을 실제 작업에서 평가
2. 평가 기간 중 "내장으로 부족했던 구체적 사례" 기록
3. 사례가 축적되면 OMC 도입 재검토, 없으면 B안 확정
