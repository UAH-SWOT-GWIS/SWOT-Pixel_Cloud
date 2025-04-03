import json
import asyncio
from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        json_message = json.dumps(message)
        for connection in self.active_connections:
            try:
                await connection.send_text(json_message)
            except:
                self.disconnect(connection)

    async def send_message(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                self.disconnect(connection)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except:
            self.disconnect(websocket)

async def connect(websocket: WebSocket, manager: ConnectionManager):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"Unrecognized message: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def send_message(message: str, broadcast: bool, manager: ConnectionManager):
    if broadcast:
        await manager.broadcast({"message": message})
    else:
        await manager.send_message(message)
