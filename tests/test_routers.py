import pytest
import uuid

from sqlalchemy import select

from app.models import Balance, Merchant
from app.schemas import PaymentCreate
from app import crud
from app.main import app
from app.database import get_db
from app.sign import make_signature


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


@pytest.mark.asyncio
async def test_webhook_completes_payment(client, db):
    # конфликт лупов
    app.dependency_overrides[get_db] = lambda: db

    merchant = await db.execute(select(Merchant).where(Merchant.name == "Test Merchant"))
    merchant_id = merchant.scalar_one().id

    payment_data = PaymentCreate(external_invoice_id="inv_999", amount="100.0",
                                 callback_url="http://test/api/v1/webhook")
    await crud.create_payment_in_db(db, merchant_id=merchant_id, payment_data=payment_data)

    response = await client.post("/api/v1/webhook", json={"id": str(uuid.uuid4()), "external_invoice_id": "inv_999",
                                                          "status": "Completed"})

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

    status = await crud.get_payment_status(db, "inv_999")
    assert status == "Completed"

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_payments(client, db):
    # тест долгий, ждем секунду

    # конфликт лупов
    app.dependency_overrides[get_db] = lambda: db

    token = "token_1"
    payment_data = {"external_invoice_id": "777", "amount": "100.50", "callback_url": "http://test/api/v1/webhook"}

    response = await client.post("/api/v1/payments",
                                 headers={"X-API-Token": token, "X-Signature": make_signature(payment_data)},
                                 json=payment_data)

    assert response.status_code == 200
    data = response.json()
    assert data["external_invoice_id"] == "777"
    assert data["status"] == "Processing"

    app.dependency_overrides.clear()
