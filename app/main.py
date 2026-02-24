from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth_routes, board_routes, task_routes
from app.websocket import websocket_routes

tags_metadata = [
    {"name": "Auth", "description": "Authentication related APIs"},
    {"name": "Boards", "description": "Board management APIs"},
    {"name": "Tasks", "description": "Task management APIs"},
]

app = FastAPI(
    title="NexTask API",
    description="Real-time Task Management Backend using FastAPI",
    version="1.0.0",
    docs_url="/api-docs",
    redoc_url="/api-redoc",
    openapi_tags=tags_metadata
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(auth_routes.router, prefix="/auth",tags=["Auth"])
app.include_router(board_routes.router, prefix="/boards", tags=["Boards"])
app.include_router(task_routes.router,prefix="/tasks",tags=["Tasks"])
app.include_router(websocket_routes.router,include_in_schema=False)
