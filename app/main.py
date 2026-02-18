from fastapi import FastAPI
from app.routes import auth_routes, board_routes
from app.websocket import websocket_routes

app = FastAPI()

app.include_router(auth_routes.router, prefix="/auth")
app.include_router(board_routes.router, prefix="/boards")
app.include_router(websocket_routes.router)
