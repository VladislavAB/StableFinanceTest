import pytest
from app.schemas import PaymentCreate
from app.crud import get_balance, create_payment_in_db, update_payment_status, deduct_balance
from app.models import Payment, Merchant
from sqlalchemy import select


@pytest.mark.asyncio
async def test_create_payment_in_db(db):
    merchant = await db.execute(select(Merchant).where(Merchant.name == "Test Merchant"))
    merchant_id = merchant.scalar_one().id

    payment_data = PaymentCreate(external_invoice_id="1", amount="250.50", callback_url="https://example.com")
    payment = await create_payment_in_db(db, merchant_id=merchant_id, payment_data=payment_data)

    assert payment.external_invoice_id == "1"
    assert payment.amount == 250.50
    assert payment.status == "Created"


@pytest.mark.asyncio
async def test_update_payment_status(db):
    merchant = await db.execute(select(Merchant).where(Merchant.name == "Test Merchant"))
    merchant_id = merchant.scalar_one().id

    payment_data = PaymentCreate(external_invoice_id="2", amount="150.50", callback_url="https://example.com")

    payment = await create_payment_in_db(db, merchant_id=merchant_id, payment_data=payment_data)
    assert payment.external_invoice_id == "2"
    assert payment.amount == 150.50
    assert payment.status == "Created"

    await update_payment_status(db, "2", "Completed")
    payment_result = await db.execute(select(Payment.status).where(Payment.external_invoice_id == "2"))
    status = payment_result.scalar_one()
    assert status == "Completed"


@pytest.mark.asyncio
async def test_deduct_balance(db):
    merchant = await db.execute(select(Merchant).where(Merchant.name == "Test Merchant"))
    merchant_id = merchant.scalar_one().id

    balance = await get_balance(db, merchant_id)
    amount = balance.amount
    assert amount == 10000.0

    await deduct_balance(db, merchant_id, 300)
    balance = await get_balance(db, merchant_id)
    amount = balance.amount
    assert amount == 9700
