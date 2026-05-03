import json
from typing import Dict, List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from jose import JWTError, jwt
from app.config import settings

router = APIRouter(tags=["websocket"])


class ConnectionManager:
    def __init__(self):
        # project_id -> list of active WebSocket connections
        self.rooms: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, project_id: str):
        await websocket.accept()
        self.rooms.setdefault(project_id, []).append(websocket)

    def disconnect(self, websocket: WebSocket, project_id: str):
        if project_id in self.rooms:
            try:
                self.rooms[project_id].remove(websocket)
            except ValueError:
                pass

    async def broadcast(self, project_id: str, event: dict):
        if project_id not in self.rooms:
            return
        dead = []
        for ws in self.rooms[project_id]:
            try:
                await ws.send_text(json.dumps(event))
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws, project_id)


manager = ConnectionManager()


@router.websocket("/ws/{project_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    project_id: str,
    token: str = Query(...),
):
    # Validate JWT before accepting
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if not user_id:
            await websocket.close(code=4001)
            return
    except JWTError:
        await websocket.close(code=4001)
        return

    await manager.connect(websocket, project_id)
    try:
        while True:
            # Keep connection alive; client sends pings
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, project_id)
