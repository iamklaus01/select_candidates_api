from pydantic import BaseModel
from typing import Hashable

from tables import Role

class UserIn(BaseModel):
    name : str
    email : str
    password : Hashable
    role: Role


class User(BaseModel):
    id : int
    name : str
    email : str
    password : Hashable
    role: Role

