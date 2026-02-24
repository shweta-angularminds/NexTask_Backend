from fastapi import APIRouter, Depends,HTTPException
from app.utils.dependencies import get_current_user
from app.db.database import db
from app.schemas.board_schema import BoardCreate,AddMember
from bson import ObjectId

router = APIRouter()

@router.get("/my-boards")
async def get_my_boards(user = Depends(get_current_user)):
    boards_cursor = db.boards.find({"owner":user["_id"]})
    boards = await boards_cursor.to_list(length=None)
    
    for board in boards:
        board["_id"] = str(board["_id"])
        board["owner"] = str(board["owner"])
        board["members"]= [str(member) for member in board["members"]]    
    
    return boards
    
@router.post("/")
async def create_board(board:BoardCreate,user=Depends(get_current_user)):
    
    new_board = {
        "title":board.title,
        "members":[user["_id"]],
        "owner":user["_id"]
    }
    
    result = await db.boards.insert_one(new_board)
    
    return{
        "message":"Board created",
        "board_id":str(result.inserted_id)
    }
    
@router.post("/{board_id}/add-member")
async def add_member(board_id:str,data:AddMember, user = Depends(get_current_user)):
    board = await db.boards.find_one({"_id":ObjectId(board_id)})
    
    if not board:
        raise HTTPException(status_code=404,detail="Board not found")
    
    if board["owner"] != user["_id"]:
        raise HTTPException(status_code=403, detail="Only owner can add member")
    
    new_user = await db.users.find_one({"email":data.email})
    
    if not new_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if new_user["_id"] in board["members"]:
        raise HTTPException(status_code=400,detail="User already a member")
    
    await db.boards.update_one(
        {"_id":ObjectId(board_id)},
        {"$push":{"members":new_user["_id"]}}
    )
    
    return {"message":"User added to board"}
    