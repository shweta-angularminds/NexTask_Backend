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

            # Just broadcast
            await manager.broadcast(board_id, data)

    except:
        manager.disconnect(board_id, websocket, user_id)
