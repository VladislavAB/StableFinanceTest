from dotenv import load_dotenv
import os

import pytest
import asyncio
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.database import Base
from app.models import Merchant, Balance

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


@pytest_asyncio.fixture()
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture()
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture()
async def engine():
    engine = create_async_engine(DATABASE_URL, echo=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine
    await engine.dispose()


@pytest_asyncio.fixture()
async def db(engine):
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(autouse=True)
async def init_test_data(db):
    merchant = Merchant(name="Test Merchant", api_token="token_1")
    db.add(merchant)
    # чтоб id взять
    await db.flush()

    balance = Balance(merchant_id=merchant.id, amount=10000.0)
    db.add(balance)

    await db.commit()
    yield
    await db.rollback()


