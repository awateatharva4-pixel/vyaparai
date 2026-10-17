from typing import List, Dict, Any
from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:
    """
    WebSocket Connection Manager for Real-Time Inventory & Metric Sync.
    Enables low-latency visual reactivity (< 50ms) across connected dashboards.
    """
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"[WEBSOCKET] Client connected. Total active: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"[WEBSOCKET] Client disconnected. Total active: {len(self.active_connections)}")

    async def broadcast(self, message: Dict[str, Any]):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection)

    def broadcast_sync(self, message: Dict[str, Any]):
        """Dispatches an async broadcast from synchronous contexts if event loop is running."""
        import asyncio
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                loop.create_task(self.broadcast(message))
        except RuntimeError:
            try:
                asyncio.run(self.broadcast(message))
            except Exception:
                pass

ws_manager = ConnectionManager()
