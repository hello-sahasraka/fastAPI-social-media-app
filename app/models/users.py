from typing import Optional
from pydantic import BaseModel


class User(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None


class UserIn(User):
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str
