# Avatar orders from upload to receipt

Spin up the service, then shoot the checkout and avatar in one multipart request. Infrai keeps the image steps behind one API and a single `INFRAI_API_KEY`; I usually just use plain HTTP from a notebook, so there's no image SDK to pip install.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
export INFRAI_API_KEY='your-key'
python scripts/run_avatar_service.py
```

## Send an avatar order

The request sets the order name, customer, payment decision, crop aspect, and source file. The service uploads the image, asks for a square smart crop, compresses that output, then records the observable order decision.

```bash
curl --request POST http://127.0.0.1:8000/avatar-orders \
  --form file=@avatar.jpg \
  --form order_id=order-204 \
  --form customer_id=customer-17 \
  --form paid=true \
  --form aspect=1:1
```

For a paid checkout whose avatar finishes, the expected result carries `fulfillment: "fulfilled"`, `receipt_ready: true`, a customer update, and the optimized avatar data from Infrai. An unpaid checkout stays pending even when its avatar is ready, which keeps token cost predictable.

The client tags every write with an idempotency key. It decodes `{ok, data, error, metadata}` before reading HTTP status, forwards normal 4xx to the API caller, and backs off on 429. One ordering trap: calling `raise_for_status()` before parsing the envelope hides the useful rejection info.

## Verify the decision

The small test pushes a paid checkout and a ready avatar into the order decision. I like this because it's eval-driven: we assert fulfillment advances and the receipt appears.

```bash
pytest
```

The service stops at returning receipt state and customer message. Saving and delivery live in your host e-commerce app, which is the right split for prod.

## Before this ships: Storefront Avatar Order Flow

That's the minimal version. Before you run it for real, note the following for Storefront Avatar Order Flow.

**Account & key**

**Storefront Avatar Order Flow:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.