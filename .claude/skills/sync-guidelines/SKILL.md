---
name: sync-guidelines
description: |
  This skill should be used when the user asks to "가이드라인 동기화",
  "sync guidelines", "문서 점검", "스킬 업데이트 확인",
  or after architecture changes to verify Skills/CLAUDE.md match the actual code.
---

# 가이드라인 동기화 점검

설계 변경 후 CLAUDE.md, Skills, Serena 메모리가 실제 코드와 일치하는지 점검한다.

## 레퍼런스 코드 분석
`src/user/`를 기준 도메인으로 읽어서 현재 실제 패턴을 파악한다:
- Base class import 경로
- 클래스 상속 구조
- 변환 패턴 (Model→DTO, DTO→Response)
- DI 패턴 (Singleton/Factory)
- 파일 구조

## 점검 대상 (3개 카테고리)
1. **CLAUDE.md ↔ 코드** — 절대 금지 규칙, 변환 패턴, Write DTO 기준
2. **Skills ↔ 코드** — 각 스킬의 파일 목록, import 경로, 패턴이 현재와 일치하는지
3. **Serena 메모리 ↔ 코드** — architecture_conventions, refactoring_status, project_overview

상세 점검 항목은 `${CLAUDE_SKILL_DIR}/references/drift-checklist.md`를 참조한다.

## 출력 형식

```
=== 가이드라인 동기화 점검 결과 ===

[OK] CLAUDE.md: 절대 금지 규칙 — 위반 없음
[DRIFT] /new-domain: Base class import — 경로 변경 감지
  → 기존: src._core.infrastructure.database.base_repository
  → 실제: src._core.database.base_repository
  → 조치: .claude/skills/new-domain/references/scaffolding-layers.md 업데이트 필요

동기화 필요: X건 / 전체: Y건
```

## DRIFT 발견 시 조치
1. 발견된 불일치 목록을 사용자에게 보여준다
2. 각 불일치에 대해 수정 제안을 한다
3. 사용자 승인 후 해당 파일을 업데이트한다
4. 업데이트 완료 후 다시 점검하여 모든 항목이 [OK]인지 확인한다

## 언제 실행해야 하는가
- 아키텍처 리팩토링 후
- Base class나 공통 모듈 변경 후
- 새로운 패턴이나 컨벤션 도입 후
- 주기적 점검 (2주에 1회 권장)
