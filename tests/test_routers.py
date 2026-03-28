import pytest
from sqlalchemy import select
from app.models import Balance

@pytest.mark.asyncio
async def test_root_endpoint(client):
    response = await client.get("/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_profile(client, db):
    token = "token_1"
    response = await client.get("/api/v1/profile", headers={"X-API-Token": token})

    data = response.json()
    merch_id = data["merchant_id"]

    assert response.status_code == 200
    assert data["name"] == "Test Merchant"

    result = await db.execute(select(Balance).where(Balance.merchant_id == merch_id))
    balance = result.scalar_one_or_none()

    assert balance.amount == 10000.0


# @pytest.mark.asyncio
# async def test_create_payments(client, db):
#     token = "token_1"
#     payment_data = {"external_invoice_id": "777", "amount": "100.50", "callback_url": "/api/v1/webhook"}
#
#     response = await client.post("/api/v1/payments",
#                                  headers={"X-API-Token": token, "X-Signature": make_signature(payment_data)},
#                                  json=payment_data)
#     assert response.status_code == 200

