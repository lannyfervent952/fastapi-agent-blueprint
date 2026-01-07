from taskiq_aws import SQSBroker

from src._core.config import settings

broker = SQSBroker(
    aws_access_key_id=settings.aws_sqs_access_key,
    aws_secret_access_key=settings.aws_sqs_secret_key,
    region_name=settings.aws_sqs_region,
    url=settings.aws_sqs_url,
)
