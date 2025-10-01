import logging
from fastapi import APIRouter, HTTPException, status, Request
from app.models.users import UserIn, UserLogin
from app.security import (
    get_user,
    get_password_hashed,
    authenticate_user,
    create_access_token,
    get_subject_for_token_type,
    create_confirmation_token
)
from app.database import database, user_table

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/user",
    tags=["users"],
)


@router.post("/", status_code=201)
async def create_user(user: UserIn, request: Request):
    if await get_user(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with that email already exists!",
        )
    logger.info("Data recieved")
    data = user.model_dump()
    data["password"] = get_password_hashed(data["password"])

    query = user_table.insert().values(data)
    # compiled = query.compile(compile_kwargs={"literal_binds": True})
    logger.debug(f"Executing query: {query}")
    await database.execute(query)

    return {""
    "message": "User Created succesfully!, Please confirm your email",
    "confirmation_email": request.url_for(
        "confirm_user", token = create_confirmation_token(user.email)
    )
    }


@router.post("/login", status_code=200)
async def login(user: UserLogin):
    await authenticate_user(user.email, user.password)
    access_token = create_access_token(user.email)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/confirm/{token}")
async def confirm_user(token:str):
    email = get_subject_for_token_type(token, "confirmation")
    query= (
        user_table.update().where(user_table.c.email == email).values(confirmed = True)
    )
    
    logger.debug(f"Executing query: {query}")
    await database.execute(query)

    return {"detail": "User confirmed"}