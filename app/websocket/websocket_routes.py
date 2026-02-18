from fastapi import WebSocket, APIRouter
from app.websocket.manager import manager
from app.db.database import db
from bson import ObjectId

router = APIRouter()

@router.websocket("/ws/{board_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, board_id: str, user_id: str):
    await manager.connect(board_id, websocket, user_id)

    try:
        while True:
            data = await websocket.receive_json()

            if data["type"] == "UPDATE_STATUS":
                await db.tasks.update_one(
                    {"_id": ObjectId(data["task_id"])},
                    {"$set": {"status": data["status"]}}
                )

                await manager.broadcast(board_id, {
                    "type": "TASK_UPDATED",
                    "task_id": data["task_id"],
                    "status": data["status"]
                })

    except:
        manager.disconnect(board_id, websocket, user_id)
