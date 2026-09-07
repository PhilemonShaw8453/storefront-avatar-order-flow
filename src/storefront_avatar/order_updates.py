from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class FulfillmentState(StrEnum):
    PENDING = "pending"
    FULFILLED = "fulfilled"


class Checkout(BaseModel):
    order_id: str = Field(min_length=1)
    customer_id: str = Field(min_length=1)
    paid: bool


class OrderUpdate(BaseModel):
    order_id: str
    customer_id: str
    fulfillment: FulfillmentState
    receipt_ready: bool
    customer_message: str


def decide_order_update(checkout: Checkout, avatar_ready: bool) -> OrderUpdate:
    fulfilled = checkout.paid and avatar_ready
    state = FulfillmentState.FULFILLED if fulfilled else FulfillmentState.PENDING
    message = "Avatar ready; order fulfilled." if fulfilled else "Order received; fulfillment pending."
    return OrderUpdate(
        order_id=checkout.order_id,
        customer_id=checkout.customer_id,
        fulfillment=state,
        receipt_ready=fulfilled,
        customer_message=message,
    )

