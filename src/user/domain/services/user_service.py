from pydantic import BaseModel

from src._core.common.security import hash_password
from src._core.domain.services.base_service import BaseService
from src.user.domain.dtos.user_dto import UserDTO
from src.user.domain.protocols.user_repository_protocol import UserRepositoryProtocol


class UserService(BaseService[UserDTO]):
    def __init__(self, user_repository: UserRepositoryProtocol) -> None:
        super().__init__(repository=user_repository)

    @staticmethod
    def _hash_entity_password(entity: BaseModel) -> BaseModel:
        if hasattr(entity, "password") and entity.password:
            return entity.model_copy(
                update={"password": hash_password(entity.password)}
            )
        return entity

    async def create_data(self, entity: BaseModel) -> UserDTO:
        return await super().create_data(entity=self._hash_entity_password(entity))

    async def update_data_by_data_id(self, data_id: int, entity: BaseModel) -> UserDTO:
        return await super().update_data_by_data_id(
            data_id=data_id, entity=self._hash_entity_password(entity)
        )
