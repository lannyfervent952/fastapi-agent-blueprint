from taskiq_aws import SQSBroker

from src._apps.worker.bootstrap import bootstrap_app
from src._apps.worker.broker import broker
from src._core.config import settings


def create_app() -> SQSBroker:

    # AWS Credential 및 Region 설정
    broker.aws_access_key_id = settings.aws_sqs_access_key
    broker.aws_secret_access_key = settings.aws_sqs_secret_key
    broker.region_name = settings.aws_sqs_region
    broker.url = settings.aws_sqs_url

    # Bootstrap 실행 (태스크 등록 및 DI 설정)
    bootstrap_app(app=broker)

    return broker


# Taskiq CLI 실행 진입점
app = create_app()
