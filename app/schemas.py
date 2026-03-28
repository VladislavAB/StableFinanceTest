from pydantic import BaseModel


class PaymentCreate(BaseModel):
    external_invoice_id: str
    amount: str
    callback_url: str


class PaymentResponse(BaseModel):
    id: str
    external_invoice_id: str
    amount: float
    callback_url: str
    status: str


class WebhookPayload(BaseModel):
    id: str
    external_invoice_id: str
    status: str


class MerchantProfile(BaseModel):
    merchant_id: int
    name: str
    balance: float
