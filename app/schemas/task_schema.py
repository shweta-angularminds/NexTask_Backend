from pydantic import BaseModel
from typing import Optional

class TaskCreate(BaseModel):
    title:str
    description:Optional[str]=None
    board_id:str
    assigned_to:Optional[str]=None
    
class TaskUpdate(BaseModel):
    title:Optional[str]=None
    description:Optional[str]=None
    status:Optional[str]=None
    assigned_to:Optional[str]=None
    
    