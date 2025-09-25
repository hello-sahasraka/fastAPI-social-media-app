import pytest
from httpx import AsyncClient

async def create_user(async_client: AsyncClient, name: str, email: str, password: str):
    return await async_client.post("/user/", json={"name": name, "email": email, "password": password})

@pytest.mark.anyio
async def test_create_user(async_client: AsyncClient):
    response = await create_user(async_client, "test", "test@example.fake", "1234")
    assert response.status_code == 201

@pytest.mark.anyio
async def test_create_user_already_exist(async_client: AsyncClient, created_user: dict):
    response = await create_user(async_client, created_user["name"], created_user["email"], created_user["password"])
    assert response.status_code == 400
