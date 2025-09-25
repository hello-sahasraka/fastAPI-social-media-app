import logging
from app.database import database, user_table 
from passlib.context import CryptContext

logger  = logging.getLogger(__name__)

pwd_contex = CryptContext(schemes=["bcrypt"])

def get_password_hashed(password: str) -> str:
    return pwd_contex.hash(password)

def verify_password(palin_password: str, hashed_password: str) -> bool:
    return pwd_contex.verify(palin_password, hashed_password)          


async def get_user(email: str):
    logger.debug("Fetching user from database", extra={"email": email})
    query = user_table.select().where(user_table.c.email == email)
    result = await database.fetch_one(query)

    if result:
        return result
