# 012. pre-commit 린팅 도구 통합: Ruff로 마이그레이션

- 상태: Accepted
- 날짜: 2026-03-23
- 관련 이슈: #58
- 관련 ADR: 010-code-quality-tools.md (Supersedes)

## 배경

ADR 010에서 pre-commit 설정을 체계화하여 6개 도구를 조합하고 있었다:
pyupgrade, autoflake, isort, Black, flake8 + plugins, bandit.

각 도구가 개별 virtualenv에서 실행되며, 도구 간 버전 호환과 설정 관리가 분산되어 있었다.

## 문제

### 1. 실행 속도

6개 도구가 순차 실행되며, 각각 별도 virtualenv를 유지한다.
초기 설치 시 수 분, 이후에도 도구별 순차 실행으로 pre-commit 전체 시간이 길다.

### 2. 설정 분산

각 도구의 설정이 `.pre-commit-config.yaml`의 `args`에 인라인으로 산재되어 있었다:

```yaml
# flake8 설정이 args에 한 줄로 압축
args:
  - --ignore=F841,E501,W503,E203,E402,F401,B008,B006,C901,SIM114,SIM910,SIM904,E704
  - --max-line-length=88
  - --max-complexity=20
  - --per-file-ignores=**/routers/*:B008,**/workflows/*:B006
```

`pyproject.toml`에 중앙 관리되지 않아 설정을 찾으려면 `.pre-commit-config.yaml`을 읽어야 했다.

### 3. 버전 관리 부담

6개 도구의 `rev`를 개별 관리해야 했다.
`pre-commit autoupdate` 시 도구 간 호환성 문제가 발생할 수 있었다.

### 4. Python 버전 의존성

Black hook에 `language_version: python3.12`가 하드코딩되어,
Python 3.13으로 업그레이드 시 hook이 실패하는 문제가 발생했다.

## 검토한 대안

### 1. 현행 유지 (6개 도구)
- 안정적이고 검증됨
- 단점: 위에 나열한 4가지 문제 지속

### 2. Ruff로 통합 (선택)
- Rust 기반, 10-100x 빠른 실행 속도
- flake8, pyupgrade, autoflake, isort, Black, bandit 규칙을 하나로 통합
- `pyproject.toml`에 설정 중앙 관리
- 1개 rev만 관리

### 3. 부분 마이그레이션 (flake8만 Ruff로)
- Black/isort는 유지하고 flake8만 교체
- 단점: 도구 수가 줄지 않아 근본적 해결이 안 됨

## 결정

**6개 린팅 도구를 Ruff 1개로 전면 교체**

### 제거한 도구

| 도구 | Ruff 대체 규칙 |
|------|-------------|
| pyupgrade | `UP` (Python 3.12+ 구문 현대화) |
| autoflake | `F` (미사용 import/변수 제거) |
| isort | `I` (import 정렬) |
| Black | `ruff format` (Black 호환 포맷팅) |
| flake8 + bugbear + comprehensions | `E`, `W`, `F`, `B`, `C4` |
| bandit | `S` (보안 검사) |

### 유지한 도구

- **pre-commit-hooks**: 일반 파일 검증 (trailing whitespace 등)
- **mypy**: 타입 체킹 (Ruff가 커버하지 않는 영역)
- **커스텀 pygrep hooks**: 아키텍처 위반 검사 4개

### 설정 구조

```toml
# pyproject.toml — 중앙 관리
[tool.ruff]
target-version = "py312"
line-length = 88
exclude = ["migrations"]

[tool.ruff.lint]
select = ["E", "W", "F", "UP", "I", "B", "C4", "SIM", "S"]
ignore = [...]  # 기존 flake8 ignore 1:1 매핑
```

```yaml
# .pre-commit-config.yaml — 실행만 담당
- repo: https://github.com/astral-sh/ruff-pre-commit
  rev: v0.15.7
  hooks:
    - id: ruff-check
      args: [--fix]
    - id: ruff-format
```

### 규칙 매핑

기존 flake8 ignore 목록을 Ruff 코드로 1:1 매핑했다.
Ruff에 존재하지 않는 규칙(W503, E203, E704, SIM904)은 제거했다.
기존 도구에서 잡지 않던 신규 규칙(SIM102, SIM117, B904, UP046, S607)은
행동 일관성을 위해 ignore에 추가했다.

## 근거

| 기준 | 6개 도구 (이전) | Ruff (현재) |
|------|-------------|------------|
| 실행 속도 | 순차 6회 실행 | Rust 기반, 10-100x 빠름 |
| 설정 위치 | .pre-commit-config.yaml args | pyproject.toml 중앙 관리 |
| 버전 관리 | 6개 rev 개별 관리 | 1개 rev |
| Python 버전 | Black에 하드코딩 필요 | target-version으로 선언적 관리 |
| 규칙 호환 | flake8 코드 체계 | 동일 코드 체계 유지 |

1. 개발 경험 개선: pre-commit 실행 시간이 체감상 크게 줄어듦
2. 설정 가독성: `pyproject.toml` 한 곳에서 모든 린팅 규칙 확인 가능
3. 유지보수 단순화: 도구 1개의 버전만 관리
4. 생태계 추세: Ruff가 Python 린팅 표준으로 자리잡는 중 (FastAPI, Pydantic, Django 등 주요 프로젝트 채택)
