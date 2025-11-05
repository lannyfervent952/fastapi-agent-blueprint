from src._core.application.dtos.base_request import BaseRequest
from src._core.application.dtos.base_response import BaseResponse
from src.user.domain.entities.user_entity import (
    CoreCreateUserEntity,
    CoreUpdateUserEntity,
    CoreUserEntity,
)


class CoreUserResponse(BaseResponse, CoreUserEntity):
    pass


class CoreCreateUserRequest(BaseRequest, CoreCreateUserEntity):
    pass


class CoreUpdateUserRequest(BaseRequest, CoreUpdateUserEntity):
    pass
