from fastapi import FastAPI, Depends, HTTPException, Request, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .database import get_db
from .models import Merchant, Balance, Payment
from .schemas import PaymentCreate, PaymentResponse, MerchantProfile, WebhookPayload
from .sign import verify_request_signature
from .redis_client import redis_lock
from . import crud
from .services import process_payment

app = FastAPI()


async def get_available_merchant(request: Request, db: AsyncSession = Depends(get_db)):
    token = request.headers.get("X-API-Token")
    if not token:
        raise HTTPException(status_code=404, detail="Нет токена")

    merchant = await crud.get_merchant_by_token(db, token)
    if not merchant:
        raise HTTPException(status_code=404, detail="Неправельный токен")

    # чтобы гет получать без подписи
    if request.method != "GET":
        await verify_request_signature(request)

    return merchant


@app.get("/")
async def root():
    return {"message": "Платёжный шлюз запущен"}


@app.get("/api/v1/profile", response_model=MerchantProfile)
async def get_profile(merchant: Merchant = Depends(get_available_merchant), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Balance).where(Balance.merchant_id == merchant.id))
    balance_obj = result.scalar_one_or_none()
    balance = float(balance_obj.amount) if balance_obj and balance_obj.amount is not None else 0.0
    return MerchantProfile(merchant_id=merchant.id, name=merchant.name, balance=balance)


@app.post("/api/v1/payments", response_model=PaymentResponse)
async def create_payments(payment_data: PaymentCreate, background_tasks: BackgroundTasks,
                         db: AsyncSession = Depends(get_db),
                         merchant: Merchant = Depends(get_available_merchant)):

    amount = float(payment_data.amount)
    async with redis_lock(f"balance_lock:{merchant.id}", expire=5):
        if not await crud.check_enough_balance(db, merchant.id, amount):
            raise HTTPException(status_code=404, detail="Недостаточно средств на балансе")

        payment = await crud.create_payment_in_db(db, merchant.id, payment_data)

    await process_payment(db, payment, background_tasks)

    return PaymentResponse(
        id=str(payment.id),
        external_invoice_id=payment.external_invoice_id,
        amount=payment.amount,
        callback_url=payment.callback_url,
        status=payment.status)


@app.post("/api/v1/webhook")
async def provider_webhook(payload: WebhookPayload, db: AsyncSession = Depends(get_db)):
    external_invoice_id = payload.external_invoice_id
    new_status = payload.status
    old_status = await crud.get_payment_status(db, external_invoice_id)

    if not external_invoice_id or new_status not in ["Completed", "Canceled"]:
        raise HTTPException(status_code=404, detail="Неверные данные вебхука")

    # тут я бы пихнул update_payment_status и deduct_balance в транзакцию
    if old_status != "Completed" and new_status == "Completed":
        await crud.update_payment_status(db=db, external_invoice_id=external_invoice_id, status=new_status)
        result = await db.execute(
            select(Payment.merchant_id, Payment.amount).
            where(Payment.external_invoice_id == external_invoice_id))

        payment_data = result.fetchone()
        if payment_data:
            merchant_id = payment_data.merchant_id
            amount = float(payment_data.amount)
            await crud.deduct_balance(db, merchant_id, amount)

    return {"status": "ok"}
