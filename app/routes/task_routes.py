from fastapi import APIRouter,Depends,HTTPException
from bson import ObjectId
from datetime import datetime
from app.db.database import db
from app.schemas.task_schema import TaskCreate,TaskUpdate
from app.utils.dependencies import get_current_user
from app.websocket.manager import manager


router = APIRouter()


#Create Task
@router.post("/")
async def create_task(task:TaskCreate,user=Depends(get_current_user)):
    
    board=await db.boards.find_one({"_id":ObjectId(task.board_id)})
    
    if not board or user["_id"] not in board["members"]:
        raise HTTPException(status_code=403,detail="Not Allowed")
    
    new_task = {
        "title":task.title,
        "description":task.description,
        "status":"todo",
        "board_id":ObjectId(task.board_id),
        "assigned_to":ObjectId(task.assigned_to) if task.assigned_to else None,
        "created_by":user["_id"],
        "created_at":datetime.utcnow()
    }    
    
    result = await db.tasks.insert_one(new_task)
    
    await manager.broadcast(task.board_id, {
        "type": "TASK_CREATED",
        "task": {
            "title": task.title,
            "status": "todo"
        }
    })

    
    return {"message":"Task created","task_id":str(result.inserted_id)}


#Get All Tasks by Board
@router.get("/{board_id}")
async def get_tasks(board_id:str, user=Depends(get_current_user)):
    board= await db.boards.find_one({"_id":ObjectId(board_id)})
    
    if not board or user["_id"] not in board["members"]:
        raise HTTPException(status_code=403,detail="Not Allowed")
    
    tasks = []
    async for task in db.tasks.find({"board_id":ObjectId(board_id)}):
        task["_id"] = str(task["_id"])
        task["board_id"] = str(task["board_id"])
        if task["assigned_to"]:
            task["assigned_to"]  = str(task["assigned_to"])
            
        tasks.append(serialize_task(task))
        
    return tasks



async def check_permission(user,task):
    if user["role"] == "admin":
        return True
    
    if task["assigned_to"] and task["assigned_to"] == user["_id"]:
        return True
    
    return False


@router.put("/{task_id}")
async def update_task(task_id:str,updated:TaskUpdate,user=Depends(get_current_user)):
    task = await db.tasks.find_one({"_id":ObjectId(task_id)})
    
    if not task:
        raise HTTPException(status_code=404,detail="Task not found")
    
    allowed = await check_permission(user,task)
    
    if not allowed:
        raise HTTPException(status_code=403,detail="Not Allowed")

    update_data = {k:v for k, v in updated.model_dump().items() if v is not None}
    
    if "assigned_to" in update_data:
        update_data["assigned_to"] = ObjectId(update_data["assigned_to"])
        
    await db.tasks.update_one(
        {"_id":ObjectId(task_id)},
        {"$set":update_data}
    )
    
    await manager.broadcast(str(task["board_id"]), {
        "type": "TASK_UPDATED",
        "task_id": task_id,
        "updates": update_data
    })

    
    return {"message":"Task updated"}


@router.delete("/{task_id}")
async def delete_task(task_id:str,user=Depends(get_current_user)):
    task = await db.tasks.find_one({"_id":ObjectId(task_id)})
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if user["role"] != "admin" and task["created_by"] != user["_id"]:
        raise HTTPException(status_code=403,detail="Not Allowed")
    
    await db.tasks.delete_one({"_id":ObjectId(task_id)})
    
    await manager.broadcast(str(task["board_id"]), {
        "type": "TASK_DELETED",
        "task_id": task_id
    })

    
    return {"message":"Task deleted"}



def serialize_task(task):
    return {
        "_id": str(task["_id"]),
        "title": task["title"],
        "description": task.get("description"),
        "status": task["status"],
        "board_id": str(task["board_id"]),
        "assigned_to": str(task["assigned_to"]) if task.get("assigned_to") else None,
        "created_by": str(task["created_by"]),
        "created_at": task["created_at"]
    }
