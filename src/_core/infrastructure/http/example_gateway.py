from typing import Any

from src._core.infrastructure.http.base_http_gateway import BaseHttpGateway
from src._core.infrastructure.http.http_client import HttpClient


class ExampleApiGateway(BaseHttpGateway):
    def __init__(self, http_client: HttpClient, base_url: str, token: str) -> None:
        super().__init__(http_client=http_client, base_url=base_url)
        self.token = token

    def _get_headers(self) -> dict[str, str]:
        """인증 토큰이 포함된 기본 헤더를 반환합니다."""
        return {"Authorization": f"Bearer {self.token}"}

    async def get_data(self, resource_id: str) -> dict[str, Any]:
        """리소스 단건 조회"""
        return await self._get(f"/resources/{resource_id}")

    async def create_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """리소스 생성"""
        return await self._post("/resources", json=data)

    async def update_data(
        self, resource_id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """리소스 전체 수정"""
        return await self._put(f"/resources/{resource_id}", json=data)

    async def delete_data(self, resource_id: str) -> bool:
        """리소스 삭제"""
        return await self._delete(f"/resources/{resource_id}")
