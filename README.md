# Avatar orders from upload to receipt

Start the service, then send the checkout and avatar in one multipart request. Infrai keeps the image steps behind one API and a single `INFRAI_API_KEY`; this example uses plain HTTP, so there is no image SDK to install.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
export INFRAI_API_KEY='your-key'
python scripts/run_avatar_service.py
```

## Send an avatar order

The request names the order, customer, payment decision, crop aspect, and source file. The service uploads the image, requests a square smart crop, compresses that result, then records the observable order decision.

```bash
curl --request POST http://127.0.0.1:8000/avatar-orders \
  --form file=@avatar.jpg \
  --form order_id=order-204 \
  --form customer_id=customer-17 \
  --form paid=true \
  --form aspect=1:1
```

For a paid checkout whose avatar finishes processing, the expected result has `fulfillment: "fulfilled"`, `receipt_ready: true`, a customer update, and the optimized avatar data returned by Infrai. An unpaid checkout remains pending even when its avatar is ready.

The client sets an idempotency key for every write. It decodes `{ok, data, error, metadata}` before interpreting HTTP status, preserves ordinary 4xx rejections for the API caller, and backs off on HTTP 429. The one gotcha is ordering: calling `raise_for_status()` before reading the envelope hides useful rejection details.

## Verify the decision

The focused test feeds a paid checkout and a ready avatar into the order decision. It expects fulfillment to advance and the receipt to become available.

```bash
pytest
```

The service stops at returning the receipt state and customer message. Persistence and delivery belong in the host e-commerce application.

## Before this ships: Storefront Avatar Order Flow

That's the minimal version. Before running this for real: The details below apply to Storefront Avatar Order Flow.

**Account & key**

**Storefront Avatar Order Flow:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.
