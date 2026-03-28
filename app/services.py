import asyncio
import uuid
from fastapi import BackgroundTasks
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from .crud import update_payment_status


async def process_payment(db: AsyncSession, payment, background_tasks: BackgroundTasks):
    await asyncio.sleep(1)
    provider_payment_id = uuid.uuid4()

    await update_payment_status(
        db=db,
        external_invoice_id=payment.external_invoice_id,
        provider_payment_id=provider_payment_id,
        status="Processing")

    background_tasks.add_task(
        send_fake_webhook,
        external_invoice_id=payment.external_invoice_id,
        provider_payment_id=str(provider_payment_id),
        callback_url=payment.callback_url)


async def send_fake_webhook(external_invoice_id: str, provider_payment_id: str, callback_url: str):
    await asyncio.sleep(2)
    status = "Completed"

    payload = {"id": provider_payment_id, "external_invoice_id": external_invoice_id, "status": status}

    async with httpx.AsyncClient() as client:
        try:
            await client.post(callback_url, json=payload)
            print(f"Вэбхук отправлен. Ардес: {callback_url}, Статус: {status}")
        except Exception as e:
            print(f"Ошибка отправки вэбхука: {e}")
