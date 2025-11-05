from src._core.infrastructure.database.base_repository import BaseRepository
from src._core.infrastructure.database.database import Database
from src.user.domain.entities.user_entity import (
    CoreCreateUserEntity,
    CoreUpdateUserEntity,
    CoreUserEntity,
)
from src.user.infrastructure.database.models.user_model import UserModel


class UserRepository(
    BaseRepository[CoreCreateUserEntity, CoreUserEntity, CoreUpdateUserEntity]
):
    def __init__(self, database: Database) -> None:
        super().__init__(
            database=database,
            model=UserModel,
            create_entity=CoreCreateUserEntity,
            return_entity=CoreUserEntity,
            update_entity=CoreUpdateUserEntity,
        )
