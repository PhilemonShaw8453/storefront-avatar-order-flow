from __future__ import annotations

import os
from typing import Annotated, Any
from uuid import uuid4

import httpx
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from .infrai_images import InfraiError, InfraiImages
from .order_updates import Checkout, OrderUpdate, decide_order_update


class AvatarOrderResult(BaseModel):
    avatar: Any
    order_update: OrderUpdate


def create_service(*, transport: httpx.AsyncBaseTransport | None = None) -> FastAPI:
    service = FastAPI(title="Storefront avatar order flow")

    @service.post("/avatar-orders", response_model=AvatarOrderResult)
    async def process_avatar_order(
        file: Annotated[UploadFile, File()],
        order_id: Annotated[str, Form()],
        customer_id: Annotated[str, Form()],
        paid: Annotated[bool, Form()],
        aspect: Annotated[str, Form()] = "1:1",
    ) -> AvatarOrderResult:
        api_key = os.environ.get("INFRAI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=503, detail="INFRAI_API_KEY is required")

        request_id = str(uuid4())
        checkout = Checkout(order_id=order_id, customer_id=customer_id, paid=paid)
        try:
            async with InfraiImages(api_key, transport=transport) as images:
                uploaded = await images.upload(await file.read(), file.filename or "avatar", request_id)
                cropped = await images.smart_crop(uploaded, aspect, request_id)
                optimized = await images.compress(cropped, request_id)
        except InfraiError as exc:
            client_status = exc.status_code if 400 <= exc.status_code < 500 else 502
            raise HTTPException(
                status_code=client_status,
                detail={"code": exc.code, "error": exc.detail},
            ) from exc

        return AvatarOrderResult(
            avatar=optimized,
            order_update=decide_order_update(checkout, avatar_ready=True),
        )

    return service


app = create_service()

