from __future__ import annotations

from typing import TYPE_CHECKING

from src._core.exceptions.base_exception import BaseCustomException

if TYPE_CHECKING:
    from src._core.domain.value_objects.dynamo_key import DynamoKey


class DynamoDBException(BaseCustomException):
    """Base exception for DynamoDB operations."""

    pass


class DynamoDBNotFoundException(DynamoDBException):
    def __init__(self, *, key: DynamoKey, table: str) -> None:
        super().__init__(
            status_code=404,
            message=f"Item not found in '{table}' with key {key}",
            error_code="DYNAMODB_NOT_FOUND",
        )


class DynamoDBConditionFailedException(DynamoDBException):
    def __init__(self, message: str = "Condition check failed") -> None:
        super().__init__(
            status_code=409,
            message=message,
            error_code="DYNAMODB_CONDITION_FAILED",
        )


class DynamoDBThrottlingException(DynamoDBException):
    def __init__(self) -> None:
        super().__init__(
            status_code=429,
            message="DynamoDB throughput exceeded",
            error_code="DYNAMODB_THROTTLED",
        )
