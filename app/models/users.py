from typing import Optional
from pydantic import BaseModel

class User(BaseModel):
    id: Optional[int] = None
    name: str

class UserIn(User):
    email: str
    password: str