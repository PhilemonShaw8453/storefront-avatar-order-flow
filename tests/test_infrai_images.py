import httpx
import pytest

from storefront_avatar.infrai_images import InfraiImages


@pytest.mark.asyncio
async def test_smart_crop_sends_the_typed_boundary() -> None:
    async def accept(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.headers["Authorization"] == "Bearer test-key"
        assert request.headers["Idempotency-Key"] == "request-1:crop"
        assert request.content == b'{"image":"image-reference","aspect":"1:1"}'
        return httpx.Response(200, json={"ok": True, "data": "cropped-image", "error": None, "metadata": {}})

    async with InfraiImages("test-key", transport=httpx.MockTransport(accept)) as images:
        result = await images.smart_crop("image-reference", "1:1", "request-1")

    assert result == "cropped-image"
