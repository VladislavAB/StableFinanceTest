from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Float, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.sql import func
from datetime import datetime
from .database import Base


class Merchant(Base):
    __tablename__ = "merchants"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    api_token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)

    # связи
    balance: Mapped["Balance"] = relationship(back_populates="merchant")
    payments: Mapped[list["Payment"]] = relationship(back_populates="merchant")


class Balance(Base):
    __tablename__ = "balances"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    merchant_id: Mapped[int] = mapped_column(ForeignKey("merchants.id"), unique=True)
    amount: Mapped[float] = mapped_column(Float, default=1000.0)

    # связь
    merchant: Mapped["Merchant"] = relationship(back_populates="balance")


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    merchant_id: Mapped[int] = mapped_column(ForeignKey("merchants.id"))
    external_invoice_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    provider_payment_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True, unique=True)
    amount: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(20), default="Created")
    callback_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # связь
    merchant: Mapped["Merchant"] = relationship(back_populates="payments")
