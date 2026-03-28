"""init - create tables + test data

Revision ID: 6b6b9353897e
Revises:
Create Date: 2026-03-27 15:35:37.573518
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = '6b6b9353897e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'merchants',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('api_token', sa.String(255), unique=True, nullable=False),
    )

    op.create_table(
        'balances',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('merchant_id', sa.Integer(), sa.ForeignKey('merchants.id'), unique=True),
        sa.Column('amount', sa.Float(), default=1000.0),
    )

    op.create_table(
        'payments',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('merchant_id', sa.Integer(), sa.ForeignKey('merchants.id')),
        sa.Column('external_invoice_id', sa.String(50), unique=True),
        sa.Column('provider_payment_id', UUID(as_uuid=True), nullable=True, unique=True),
        sa.Column('amount', sa.Float()),
        sa.Column('status', sa.String(20), default="Created"),
        sa.Column('callback_url', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('payments')
    op.drop_table('balances')
    op.drop_table('merchants')
