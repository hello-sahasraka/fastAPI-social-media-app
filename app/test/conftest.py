import os
from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from app.database import database, user_table

os.environ["ENV_STATE"] = "test"

from app.main import app


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
def client() -> Generator:
    yield TestClient(app)


@pytest.fixture(autouse=True)
async def db() -> AsyncGenerator:
    await database.connect()
    async with database.transaction(force_rollback=True):
        yield
    await database.disconnect()


@pytest.fixture()
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture()
async def created_user(async_client: AsyncClient) -> dict:
    user_details = {"name": "test", "email": "test@example.netfake", "password": "1234"}
    await async_client.post("/user/", json=user_details)
    query = user_table.select().where(user_table.c.email == user_details["email"])
    user = await database.fetch_one(query)
    user_details["id"] = user["id"]
    return user_details

@pytest.fixture()
async def confirm_user(created_user: dict) -> dict:
    query = (
        user_table.update().where(user_table.c.email == created_user["email"]).values(confirmed = True)
    )
    await database.execute(query)
    return created_user

@pytest.fixture()
async def logged_in_token(async_client: AsyncClient, confirm_user: dict) -> str:
    response = await async_client.post("/user/login", json=confirm_user)

    return response.json()["access_token"]
