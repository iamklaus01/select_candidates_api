from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from tables import Role

class UserIn(BaseModel):
    name : str
    email : str
    password : str
    role: Role


class User(BaseModel):
    id : int
    name : str
    email : str
    password : str
    role: Role
    active: bool
    created_at: datetime

class LoginSchema(BaseModel):
    email : str
    password : str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
