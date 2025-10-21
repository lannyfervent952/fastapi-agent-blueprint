from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import aioboto3
from types_aiobotocore_s3.client import S3Client as BotoS3Client


class S3Client:
    def __init__(
        self,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        region_name: str,
    ) -> None:
        self.session = aioboto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
        )

    @asynccontextmanager
    async def client(self) -> AsyncGenerator[BotoS3Client, None]:
        async with self.session.client("s3") as s3_client:
            yield s3_client
