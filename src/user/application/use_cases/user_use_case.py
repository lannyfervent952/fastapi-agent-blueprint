from src._core.application.use_cases.base_use_case import BaseUseCase
from src.user.domain.entities.user_entity import (
    CoreCreateUserEntity,
    CoreUpdateUserEntity,
    CoreUserEntity,
)
from src.user.domain.services.user_service import UserService


class UserUseCase(
    BaseUseCase[CoreCreateUserEntity, CoreUserEntity, CoreUpdateUserEntity]
):
    def __init__(self, user_service: UserService) -> None:
        super().__init__(
            base_service=user_service,
            create_entity=CoreCreateUserEntity,
            return_entity=CoreUserEntity,
            update_entity=CoreUpdateUserEntity,
        )
