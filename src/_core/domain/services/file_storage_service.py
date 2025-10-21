from datetime import datetime
from typing import BinaryIO

from src._core.infrastructure.storage.s3_storage import S3Storage


class FileStorageService:
    """파일 스토리지 도메인 서비스"""

    def __init__(self, s3_storage: S3Storage) -> None:
        self.s3_storage = s3_storage

    async def upload_user_file(
        self, user_id: int, file_obj: BinaryIO | bytes, filename: str
    ) -> str:
        """사용자 파일 업로드"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        key = f"users/{user_id}/{timestamp}_{filename}"

        # 파일 타입 추론
        content_type = self._get_content_type(filename)

        await self.s3_storage.upload_file(
            file_obj=file_obj, key=key, content_type=content_type
        )
        return key

    async def download_user_file(self, user_id: int, key: str) -> bytes:
        """사용자 파일 다운로드 (권한 체크 포함)"""
        # 간단한 권한 체크: key가 해당 user_id의 경로인지 확인
        if not key.startswith(f"users/{user_id}/"):
            raise PermissionError(f"User {user_id} cannot access file {key}")

        return await self.s3_storage.download_file(key)

    async def delete_user_file(self, user_id: int, key: str) -> bool:
        """사용자 파일 삭제 (권한 체크 포함)"""
        if not key.startswith(f"users/{user_id}/"):
            raise PermissionError(f"User {user_id} cannot delete file {key}")

        return await self.s3_storage.delete_file(key)

    async def get_user_files(self, user_id: int) -> list[str]:
        """사용자의 모든 파일 목록 조회"""
        prefix = f"users/{user_id}/"
        return await self.s3_storage.list_files(prefix)

    async def get_file_download_url(self, user_id: int, key: str) -> str:
        """파일 다운로드 URL 생성"""
        if not key.startswith(f"users/{user_id}/"):
            raise PermissionError(f"User {user_id} cannot access file {key}")

        return await self.s3_storage.get_file_url(key)

    def _get_content_type(self, filename: str) -> str:
        """파일 확장자로 Content-Type 추론"""
        extension = filename.lower().split(".")[-1]
        content_types = {
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "png": "image/png",
            "gif": "image/gif",
            "pdf": "application/pdf",
            "txt": "text/plain",
            "json": "application/json",
        }
        return content_types.get(extension, "application/octet-stream")
