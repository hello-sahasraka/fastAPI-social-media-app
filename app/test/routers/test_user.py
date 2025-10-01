import pytest
from httpx import AsyncClient
from fastapi import Request


async def create_user(async_client: AsyncClient, name: str, email: str, password: str):
    return await async_client.post(
        "/user/", json={"name": name, "email": email, "password": password}
    )


@pytest.mark.anyio
async def test_create_user(async_client: AsyncClient):
    response = await create_user(async_client, "test", "test@example.fake", "1234")
    assert response.status_code == 201


@pytest.mark.anyio
async def test_create_user_already_exist(async_client: AsyncClient, created_user: dict):
    response = await create_user(
        async_client,
        created_user["name"],
        created_user["email"],
        created_user["password"],
    )
    assert response.status_code == 400

@pytest.mark.anyio
async def test_confirm_user(async_client: AsyncClient, mocker):
    spy = mocker.spy(Request, "url_for")
    await create_user(async_client, "test", "test@gmail.com", "1234")
    confirmation_url = str(spy.spy_return)

    response = await async_client.post(confirmation_url)
    assert response.status_code == 200
    assert "User confirmed" in response.json()["detail"]

@pytest.mark.anyio
async def test_confirm_user_invalid_token(async_client: AsyncClient):
    response = await  async_client.post("/user/confirm/invalid_token")

    assert response.status_code == 401

@pytest.mark.anyio
async def test_confirm_user_expired_token(async_client: AsyncClient, mocker):
    mocker.patch("app.security.confirmn_token_expire_minutes", return_value = -1)
    spy = mocker.spy(Request, "url_for")
    await create_user(async_client, "test", "test@gmail.com", "1234")
    confirmation_url = str(spy.spy_return)

    response = await async_client.post(confirmation_url)
    assert response.status_code == 401
    assert "Token has expired" in response.json()["detail"]

@pytest.mark.anyio
async def test_login_user_not_exist(async_client: AsyncClient):
    response = await async_client.post(
        "/user/login", json={"email": "notexist@example.com", "password": "wrongpass"}
    )

    assert response.status_code == 401

@pytest.mark.anyio
async def test_login_user_not_confirmed(async_client: AsyncClient, created_user: dict):
    response = await async_client.post(
        "/user/login",
        json={"email": created_user["email"], "password": created_user["password"]},
    )

    assert response.status_code == 401


@pytest.mark.anyio
async def test_login_user(async_client: AsyncClient, confirm_user: dict):
    response = await async_client.post(
        "/user/login",
        json={"email": confirm_user["email"], "password": confirm_user["password"]},
    )

    assert response.status_code == 200
