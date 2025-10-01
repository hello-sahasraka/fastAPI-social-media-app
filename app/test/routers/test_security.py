import pytest
from app import security
from jose import jwt
from app.config import config

ALGORITHM = "HS256"

@pytest.mark.anyio
async def test_access_token_expire_minutes():
    assert security.access_token_expire_minutes() == 60


@pytest.mark.anyio
async def test_confirm_token_expire_minutes():
    assert security.confirmn_token_expire_minutes() == 1440


@pytest.mark.anyio
async def test_create_access_token():
    token = security.create_access_token("hello")
    assert {"sub": "hello", "type": "access"}.items() <= jwt.decode(
        token, key=config.SECRET_KEY, algorithms=[security.ALGORITHM]
    ).items()


@pytest.mark.anyio
async def test_create_confirmation_token():
    token = security.create_confirmation_token("hello")
    assert {"sub": "hello", "type": "confirmation"}.items() <= jwt.decode(
        token, key=config.SECRET_KEY, algorithms=[security.ALGORITHM]
    ).items()

def test_get_subject_for_token_type_valid_confirmation():
    email = "test@example.com"
    token = security.create_confirmation_token(email)

    assert email == security.get_subject_for_token_type(token, "confirmation")
    
def test_get_subject_for_token_type_valid_access():
    email = "test@example.com"
    token = security.create_access_token(email)

    assert email == security.get_subject_for_token_type(token, "access")


def test_get_subject_for_token_type_expired(mocker):
    mocker.patch("app.security.access_token_expire_minutes", return_value=-1)
    email = "test@example.com"
    token = security.create_access_token(email)
    with  pytest.raises(security.HTTPException) as exe_info:
        security.get_subject_for_token_type(token, "access")
        assert "Token has expired" == exe_info.value.detail

def test_get_subject_for_token_type_invalid_token(mocker):
    token = "Invalid token"
    with  pytest.raises(security.HTTPException) as exe_info:
        security.get_subject_for_token_type(token, "access")
        assert "Invalid token" == exe_info.value.detail

def test_get_subject_for_token__type_missing_sub():
    email = "test@example.com"
    token = security.create_access_token(email)

    payload = jwt.decode(token, key=config.SECRET_KEY, algorithms=ALGORITHM)

    del payload["sub"]

    token = jwt.encode(payload, key=config.SECRET_KEY, algorithm=ALGORITHM)

    with pytest.raises(security.HTTPException) as exe_info:
        security.get_subject_for_token_type(token, "access")

        assert "Token is missing 'sub field" == exe_info.value.detail


def test_get_subject_for_token_type_wrong_type():
    email = "test@example.com"
    token = security.create_confirmation_token(email)

    with pytest.raises(security.HTTPException) as exe_info:
        security.get_subject_for_token_type(token, "access")

        assert "Token has incorrect type, expected 'access'" == exe_info.value.detail


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


@pytest.mark.anyio
async def test_authenticate_user(created_user: dict):
    user = await security.authenticate_user(
        created_user["email"], created_user["password"]
    )

    assert user["email"] == created_user["email"]


@pytest.mark.anyio
async def test_authenticate_user_not_found():
    with pytest.raises(security.HTTPException):
        await security.authenticate_user("dayashantha", "1234")


@pytest.mark.anyio
async def test_authenticate_user_wrong_password(created_user: dict):
    with pytest.raises(security.HTTPException):
        await security.authenticate_user(created_user["email"], "wrong_pass")


@pytest.mark.anyio
async def test_get_current_user(created_user: dict):
    token = security.create_access_token(created_user["email"])
    user = await security.get_current_user(token)

    assert user["email"] == created_user["email"]


@pytest.mark.anyio
async def test_get_current_user_invalid_token():
    with pytest.raises(security.HTTPException):
        await security.get_current_user("Invalid token")


@pytest.mark.anyio
async def test_get_current_user_wrong_token_type(created_user: dict):
    token = security.create_confirmation_token(created_user["email"])

    with pytest.raises(security.HTTPException):
        await security.get_current_user(token)
