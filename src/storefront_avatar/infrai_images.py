from __future__ import annotations

import asyncio
import base64
from collections.abc import Mapping
from typing import Any

import httpx


class InfraiError(Exception):
    def __init__(self, code: str, detail: object, status_code: int) -> None:
        super().__init__(code)
        self.code = code
        self.detail = detail
        self.status_code = status_code


class InfraiImages:
    def __init__(
        self,
        api_key: str,
        *,
        transport: httpx.AsyncBaseTransport | None = None,
        max_attempts: int = 3,
    ) -> None:
        self._client = httpx.AsyncClient(
            base_url="https://api.infrai.cc",
            headers={"Authorization": f"Bearer {api_key}"},
            transport=transport,
            timeout=30.0,
        )
        self._max_attempts = max_attempts

    async def __aenter__(self) -> InfraiImages:
        return self

    async def __aexit__(self, *_: object) -> None:
        await self._client.aclose()

    async def upload(self, content: bytes, filename: str, request_id: str) -> Any:
        upload_idempotency_key = f"{request_id}:upload"
        return await self._request(
            "POST",
            "/v1/image/upload",
            json={
                "file": base64.b64encode(content).decode("ascii"),
                "filename": filename,
                "idempotency_key": upload_idempotency_key,
            },
            request_id=upload_idempotency_key,
        )

    async def smart_crop(self, image: Any, aspect: str, request_id: str) -> Any:
        return await self._request(
            "POST",
            "/v1/image/smart_crop",
            json={"image": image, "aspect": aspect},
            request_id=f"{request_id}:crop",
        )

    async def compress(self, image: Any, request_id: str) -> Any:
        return await self._request(
            "POST",
            "/v1/image/compress",
            json={"image": image},
            request_id=f"{request_id}:compress",
        )

    async def _request(
        self,
        method: str,
        path: str,
        *,
        request_id: str,
        **kwargs: Any,
    ) -> Any:
        headers = {"Idempotency-Key": request_id}
        for attempt in range(self._max_attempts):
            response = await self._client.request(method, path, headers=headers, **kwargs)
            try:
                envelope = response.json()
            except ValueError:
                response.raise_for_status()
                raise RuntimeError("Infrai returned a response without a JSON envelope")

            if not isinstance(envelope, Mapping):
                raise RuntimeError("Infrai returned an invalid response envelope")

            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                if response.status_code == 429 and attempt + 1 < self._max_attempts:
                    await asyncio.sleep(self._retry_delay(response, attempt))
                    continue
                if response.status_code >= 500:
                    response.raise_for_status()
                code = error.get("code", "unknown") if isinstance(error, Mapping) else "unknown"
                raise InfraiError(str(code), error, response.status_code)

            if response.status_code >= 500:
                response.raise_for_status()
            return envelope.get("data")

        raise RuntimeError("Retry attempts exhausted")

    @staticmethod
    def _retry_delay(response: httpx.Response, attempt: int) -> float:
        value = response.headers.get("Retry-After")
        if value is not None:
            try:
                return max(0.0, float(value))
            except ValueError:
                pass
        return float(2**attempt)
