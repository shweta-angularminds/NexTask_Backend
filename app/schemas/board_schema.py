from pydantic import BaseModel,EmailStr
from typing import Optional

class BoardCreate(BaseModel):
    title: str


class AddMember(BaseModel):
    email:EmailStr