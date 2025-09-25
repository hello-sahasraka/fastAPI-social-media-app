import pytest
from app import security

@pytest.mark.anyio
async def test_get_user(created_user: dict):
    user = await security.get_user(created_user["email"])
    
    assert user["email"] == created_user["email"]

@pytest.mark.anyio
async def test_get_user_not_found():
    user = await security.get_user("test@notfound.com")

    assert user is None

@pytest.mark.anyio
async def test_password_hashed():
    password = "password"

    assert security.verify_password(password, security.get_password_hashed(password))