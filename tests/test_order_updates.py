from storefront_avatar.order_updates import Checkout, FulfillmentState, decide_order_update


def test_paid_checkout_with_ready_avatar_releases_receipt() -> None:
    update = decide_order_update(
        Checkout(order_id="order-204", customer_id="customer-17", paid=True),
        avatar_ready=True,
    )

    assert update.fulfillment is FulfillmentState.FULFILLED
    assert update.receipt_ready is True
    assert update.customer_message == "Avatar ready; order fulfilled."


def test_unpaid_checkout_stays_pending_after_avatar_processing() -> None:
    update = decide_order_update(
        Checkout(order_id="order-205", customer_id="customer-18", paid=False),
        avatar_ready=True,
    )

    assert update.fulfillment is FulfillmentState.PENDING
    assert update.receipt_ready is False

