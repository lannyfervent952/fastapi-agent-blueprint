from src._core.domain.services.base_service import BaseService
from src.user.domain.entities.user_entity import (
    CoreCreateUserEntity,
    CoreUpdateUserEntity,
    CoreUserEntity,
)
from src.user.infrastructure.repositories.user_repository import UserRepository


class UserService(
    BaseService[CoreCreateUserEntity, CoreUserEntity, CoreUpdateUserEntity]
):
    def __init__(self, user_repository: UserRepository) -> None:
        super().__init__(
            base_repository=user_repository,
            create_entity=CoreCreateUserEntity,
            return_entity=CoreUserEntity,
            update_entity=CoreUpdateUserEntity,
        )
