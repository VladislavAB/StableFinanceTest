from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Merchant, Balance, Payment
from .schemas import PaymentCreate
import uuid


async def get_merchant_by_token(db: AsyncSession, token: str):
    result = await db.execute(select(Merchant).where(Merchant.api_token == token))
    return result.scalar_one_or_none()


async def get_balance(db: AsyncSession, merchant_id: int):
    result = await db.execute(select(Balance).where(Balance.merchant_id == merchant_id))
    return result.scalar_one_or_none()


async def check_enough_balance(db: AsyncSession, merchant_id: int, amount: float) -> bool:
    balance = await get_balance(db, merchant_id)
    if not balance:
        return False

    current_balance = float(balance.amount) if balance.amount is not None else 0.0
    return current_balance >= amount


async def create_payment_in_db(db: AsyncSession, merchant_id: int, payment_data: PaymentCreate):
    payment = Payment(
        merchant_id=merchant_id,
        status="Created",
        external_invoice_id=payment_data.external_invoice_id,
        amount=float(payment_data.amount),
        callback_url=payment_data.callback_url)

    db.add(payment)
    await db.commit()
    # чтобы id взятб
    await db.refresh(payment)
    return payment


async def update_payment_status(db: AsyncSession, external_invoice_id: str, status: str,
                                provider_payment_id: uuid.UUID | None = None):
    query = update(Payment).where(Payment.external_invoice_id == external_invoice_id)

    values = {"status": status}
    if provider_payment_id:
        values["provider_payment_id"] = provider_payment_id

    await db.execute(query.values(**values))
    await db.commit()


async def get_payment_status(db: AsyncSession, external_invoice_id: str):
    result = await db.execute(select(Payment.status).where(Payment.external_invoice_id == external_invoice_id))
    return result.scalar_one_or_none()


async def deduct_balance(db: AsyncSession, merchant_id: int, amount: float):
    await db.execute(update(Balance).where(Balance.merchant_id == merchant_id).values(amount=Balance.amount - amount))
    await db.commit()
