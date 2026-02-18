from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections = {}
        self.online_users = {}

    async def connect(self, board_id: str, websocket: WebSocket, user_id: str):
        await websocket.accept()

        if board_id not in self.active_connections:
            self.active_connections[board_id] = []
            self.online_users[board_id] = []

        self.active_connections[board_id].append(websocket)
        self.online_users[board_id].append(user_id)

    def disconnect(self, board_id: str, websocket: WebSocket, user_id: str):
        self.active_connections[board_id].remove(websocket)
        self.online_users[board_id].remove(user_id)

    async def broadcast(self, board_id: str, message: dict):
        for connection in self.active_connections.get(board_id, []):
            await connection.send_json(message)

manager = ConnectionManager()
