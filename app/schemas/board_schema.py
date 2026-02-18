from pydantic import BaseModel

class BoardCreate(BaseModel):
    title: str
