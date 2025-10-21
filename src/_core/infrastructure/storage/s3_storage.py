from io import BytesIO
from typing import BinaryIO

from botocore.exceptions import ClientError

from src._core.exceptions.base_exception import BaseCustomException
from src._core.infrastructure.storage.s3_client import S3Client


class S3Storage:
    def __init__(self, s3_client: S3Client, bucket_name: str) -> None:
        self.s3_client = s3_client
        self.bucket_name = bucket_name

    async def upload_file(
        self,
        file_obj: BinaryIO | bytes,
        key: str,
        content_type: str = "application/octet-stream",
    ) -> str:
        """파일 업로드"""
        try:
            async with self.s3_client.client() as client:
                if isinstance(file_obj, bytes):
                    file_obj = BytesIO(file_obj)

                await client.upload_fileobj(
                    Fileobj=file_obj,
                    Bucket=self.bucket_name,
                    Key=key,
                    ExtraArgs={"ContentType": content_type},
                )
                return key
        except ClientError as e:
            raise BaseCustomException(status_code=500, message=f"S3 upload failed: {e}")

    async def download_file(self, key: str) -> bytes:
        """파일 다운로드"""
        try:
            async with self.s3_client.client() as client:
                response = await client.get_object(Bucket=self.bucket_name, Key=key)
                async with response["Body"] as stream:
                    return await stream.read()
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                raise BaseCustomException(
                    status_code=404, message=f"File not found: {key}"
                )
            raise BaseCustomException(
                status_code=500, message=f"S3 download failed: {e}"
            )

    async def delete_file(self, key: str) -> bool:
        """파일 삭제"""
        try:
            async with self.s3_client.client() as client:
                await client.delete_object(Bucket=self.bucket_name, Key=key)
                return True
        except ClientError as e:
            raise BaseCustomException(status_code=500, message=f"S3 delete failed: {e}")

    async def file_exists(self, key: str) -> bool:
        """파일 존재 여부 확인"""
        try:
            async with self.s3_client.client() as client:
                await client.head_object(Bucket=self.bucket_name, Key=key)
                return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            raise BaseCustomException(status_code=500, message=f"S3 check failed: {e}")

    async def get_file_url(self, key: str, expires_in: int = 3600) -> str:
        """파일 presigned URL 생성"""
        try:
            async with self.s3_client.client() as client:
                url = await client.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": self.bucket_name, "Key": key},
                    ExpiresIn=expires_in,
                )
                return url
        except ClientError as e:
            raise BaseCustomException(
                status_code=500, message=f"S3 presigned URL generation failed: {e}"
            )

    async def list_files(self, prefix: str = "") -> list[str]:
        """파일 목록 조회"""
        try:
            async with self.s3_client.client() as client:
                response = await client.list_objects_v2(
                    Bucket=self.bucket_name, Prefix=prefix
                )
                if "Contents" not in response:
                    return []
                return [obj["Key"] for obj in response["Contents"]]
        except ClientError as e:
            raise BaseCustomException(status_code=500, message=f"S3 list failed: {e}")
