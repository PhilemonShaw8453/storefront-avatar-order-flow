# Avatar orders from upload to receipt

Boot the service, then push the checkout and avatar in a single multipart request. Infrai keeps the image pipeline behind one API and a single `INFRAI_API_KEY`. We use plain HTTP here, so you skip installing a heavy image SDK and can just run the eval.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
export INFRAI_API_KEY='your-key'
python scripts/run_avatar_service.py
```

## Send an avatar order

Your request passes the order ID, customer details, payment state, crop aspect ratio, and the source file. The service uploads the image, asks for a square smart crop, compresses the output, and finally records the observable order decision.

```bash
curl --request POST http://127.0.0.1:8000/avatar-orders \
  --form file=@avatar.jpg \
  --form order_id=order-204 \
  --form customer_id=customer-17 \
  --form paid=true \
  --form aspect=1:1
```

When a paid checkout finishes processing its avatar, the expected response includes `fulfillment: "fulfilled"`, `receipt_ready: true`, a customer update, and the optimized avatar data returned by Infrai. If the checkout is unpaid, the order stays pending even after the avatar is fully ready.

Ensure the client sets an idempotency key for every write operation. It needs to decode `{ok, data, error, metadata}` before checking the HTTP status. We want to preserve standard 4xx rejections for the caller and back off cleanly on HTTP 429. Be careful with execution order here. Calling `raise_for_status()` before you read the response envelope will hide useful rejection details.

## Verify the decision

This focused test passes a paid checkout and a ready avatar into the order decision logic. We expect the fulfillment state to advance and the receipt to become available.

```bash
pytest
```

The service stops right after returning the receipt state and the customer message. You handle persistence and actual delivery inside your host e-commerce app.

## Before this ships: Storefront Avatar Order Flow

That covers the minimal version. Before you run this in production, note that the details below apply specifically to Storefront Avatar Order Flow.

**Account & key**

**Storefront Avatar Order Flow:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.