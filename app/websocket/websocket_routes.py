from fastapi import WebSocket, APIRouter, WebSocketDisconnect
from jose import jwt, JWTError
from bson import ObjectId
from app.websocket.manager import manager
from app.db.database import db
from app.core.config import SECRET_KEY, ALGORITHM

router = APIRouter()

@router.websocket("/ws/{board_id}")
async def websocket_endpoint(websocket: WebSocket, board_id: str):

    # 1️. Get JWT token from query param
    token = websocket.query_params.get("token")

    if not token:
        await websocket.close(code=1008)
        return

    try:
        # 2️. Decode JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")

        if not user_id:
            await websocket.close(code=1008)
            return

        # 3️. Verify user exists
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            await websocket.close(code=1008)
            return

        # 4️. Verify board membership
        board = await db.boards.find_one({"_id": ObjectId(board_id)})
        if not board or ObjectId(user_id) not in board["members"]:
            await websocket.close(code=1008)
            return

    except JWTError:
        await websocket.close(code=1008)
        return

    # 5️. Accept connection
    await manager.connect(board_id, websocket, str(user["_id"]))

    # 6. Notify others user joined
    await manager.broadcast(board_id, {
        "type": "USER_JOINED",
        "user_id": str(user["_id"]),
        "name": user.get("name")
    })

    try:
        while True:
            data = await websocket.receive_json()
            await manager.broadcast(board_id, data)

    except WebSocketDisconnect:
        manager.disconnect(board_id, websocket, str(user["_id"]))

        await manager.broadcast(board_id, {
            "type": "USER_LEFT",
            "user_id": str(user["_id"])
        })
