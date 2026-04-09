import pytest
from taskiq import InMemoryBroker

from src._core.infrastructure.taskiq.broker import (
    CustomSQSBroker,
    create_rabbitmq_broker,
)


class TestCustomSQSBroker:
    def test_creates_instance(self):
        broker = CustomSQSBroker(
            queue_url="https://sqs.ap-northeast-2.amazonaws.com/123/test",
            aws_region="ap-northeast-2",
            aws_access_key_id="key",
            aws_secret_access_key="secret",
        )
        assert isinstance(broker, CustomSQSBroker)


class TestInMemoryBroker:
    def test_creates_instance(self):
        broker = InMemoryBroker()
        assert isinstance(broker, InMemoryBroker)


class TestCreateRabbitmqBroker:
    def test_raises_import_error_without_package(self):
        """RabbitMQ requires taskiq-aio-pika which is an optional dependency."""
        with pytest.raises((ImportError, ModuleNotFoundError)):
            create_rabbitmq_broker(url="amqp://guest:guest@localhost:5672/")
