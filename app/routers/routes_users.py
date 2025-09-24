import logging
from fastapi import APIRouter, HTTPException, status
from app.models.users import UserIn
from app.security import get_user
from app.database import database, user_table

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/user",
    tags=["users"],
)

@router.post("/", status_code=201)
async def create_user(user: UserIn):
    if await get_user(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with that email already exists!"
        )
    logger.info("Data recieved")
    data = user.model_dump()
    query = user_table.insert().values(data)

    compiled = query.compile(compile_kwargs={"literal_binds": True})
    logger.debug(f"Executing query: {compiled}")

    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}
