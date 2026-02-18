from fastapi import APIRouter, Depends
from app.utils.dependencies import get_current_user
from app.db.database import db
from app.schemas.board_schema import BoardCreate


router = APIRouter()

@router.post("/")
async def create_board(board:BoardCreate,user=Depends(get_current_user)):
    new_board = {
        "title":board.title,
        "members":[user["_id"]]
    }
    
    await db.boards.insert_one(new_board)
    return {"message":"Board created"}
