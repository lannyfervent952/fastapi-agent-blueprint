---
name: add-worker-task
argument-hint: domain_name task_name
description: |
  This skill should be used when the user asks to "태스크 추가",
  "워커 태스크", "비동기 작업 추가", "add worker task",
  "background job", "async task", "queue task", "Taskiq 태스크",
  or wants to create a new asynchronous background task for a domain.
---

# 비동기 Worker 태스크 추가

요청: $ARGUMENTS (도메인명과 태스크 설명, 예: "order process_payment")

## 분석

1. 도메인명과 태스크 목적 파악
2. 해당 도메인의 Service에 필요한 메서드가 있는지 확인
3. 없으면 `/add-api` 절차의 1~2단계(Repository → Service)를 먼저 수행

## 레퍼런스
- `src/user/interface/worker/tasks/user_test_task.py` — 태스크 패턴
- `src/user/interface/worker/bootstrap/user_bootstrap.py` — 워커 부트스트랩 패턴
- `src/_apps/worker/broker.py` — 브로커 설정

## 구현 순서

### 1. 태스크 함수 생성
`src/{name}/interface/worker/tasks/{task_name}_task.py`

```python
from dependency_injector.wiring import Provide, inject
from src._apps.worker.broker import broker
from src._core.config import settings
from src.{name}.domain.dtos.{name}_dto import {Name}DTO
from src.{name}.domain.services.{name}_service import {Name}Service
from src.{name}.infrastructure.di.{name}_container import {Name}Container

@broker.task(task_name=f"{settings.task_name_prefix}.{name}.{task_name}")
@inject
async def {task_name}_task(
    {name}_service: {Name}Service = Provide[{Name}Container.{name}_service],
    **kwargs,
) -> None:
    dto = {Name}DTO.model_validate(kwargs)
    await {name}_service.{method}(dto=dto)
```

### 2. 워커 부트스트랩 업데이트
`src/{name}/interface/worker/bootstrap/{name}_bootstrap.py`에서:
- 새 태스크 모듈을 import
- `wire(modules=[..., {task_name}_task])` 에 추가

### 3. Service 메서드 확인/추가
- 태스크가 호출할 Service 메서드가 있는지 확인
- 없으면 Service에 메서드 추가 (필요 시 Repository도)

## 핵심 규칙
- 태스크 함수는 thin adapter: `**kwargs` 받아서 DTO 변환 후 Service 호출만
- 비즈니스 로직은 반드시 Service에 위치
- Model 객체가 태스크에 노출되면 안 됨
- DI 패턴: **project-dna.md §5** 참조
- 변환 패턴: **project-dna.md §6** 참조

## 완료 후 검증
1. pre-commit 실행
2. 브로커 import 확인: `python -c "from src.{name}.interface.worker.tasks.{task_name}_task import {task_name}_task; print('OK')"`
