from typing import Any

from src._core.infrastructure.http.http_client import HttpClient


class BaseHttpGateway:
    def __init__(self, http_client: HttpClient, base_url: str) -> None:
        self.http_client = http_client
        self.base_url = base_url

    def _get_headers(self) -> dict[str, str]:
        """기본 헤더를 반환합니다. 하위 클래스에서 오버라이드 가능합니다."""
        return {}

    async def _get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """GET 요청을 수행합니다."""
        merged_headers = {**self._get_headers(), **(headers or {})}

        async with self.http_client.session() as session:
            async with session.get(
                f"{self.base_url}{endpoint}",
                params=params,
                headers=merged_headers,
            ) as response:
                response.raise_for_status()
                return await response.json()

    async def _post(
        self,
        endpoint: str,
        json: dict[str, Any] | None = None,
        data: Any | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """POST 요청을 수행합니다."""
        merged_headers = {**self._get_headers(), **(headers or {})}

        async with self.http_client.session() as session:
            async with session.post(
                f"{self.base_url}{endpoint}",
                json=json,
                data=data,
                headers=merged_headers,
            ) as response:
                response.raise_for_status()
                return await response.json()

    async def _put(
        self,
        endpoint: str,
        json: dict[str, Any] | None = None,
        data: Any | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """PUT 요청을 수행합니다."""
        merged_headers = {**self._get_headers(), **(headers or {})}

        async with self.http_client.session() as session:
            async with session.put(
                f"{self.base_url}{endpoint}",
                json=json,
                data=data,
                headers=merged_headers,
            ) as response:
                response.raise_for_status()
                return await response.json()

    async def _patch(
        self,
        endpoint: str,
        json: dict[str, Any] | None = None,
        data: Any | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """PATCH 요청을 수행합니다."""
        merged_headers = {**self._get_headers(), **(headers or {})}

        async with self.http_client.session() as session:
            async with session.patch(
                f"{self.base_url}{endpoint}",
                json=json,
                data=data,
                headers=merged_headers,
            ) as response:
                response.raise_for_status()
                return await response.json()

    async def _delete(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> bool:
        """DELETE 요청을 수행합니다."""
        merged_headers = {**self._get_headers(), **(headers or {})}

        async with self.http_client.session() as session:
            async with session.delete(
                f"{self.base_url}{endpoint}",
                params=params,
                headers=merged_headers,
            ) as response:
                response.raise_for_status()
                return True
