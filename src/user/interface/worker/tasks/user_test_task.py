from dependency_injector.wiring import Provide, inject

from src._apps.worker.broker import broker
from src._core.config import settings
from src.user.application.use_cases.user_use_case import UserUseCase
from src.user.domain.dtos.user_dto import UserDTO
from src.user.infrastructure.di.user_container import UserContainer


@broker.task(task_name=f"{settings.task_name_prefix}.user.test")
@inject
async def consume_task(
    user_use_case: UserUseCase = Provide[UserContainer.user_use_case],
    **kwargs,
) -> None:
    dto = UserDTO.model_validate(kwargs)

    await user_use_case.process_user(dto=dto)
