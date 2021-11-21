from pydantic import BaseModel
from websockets.legacy.server import WebSocketServerProtocol


class User(BaseModel):
    id: str
    clients: list[WebSocketServerProtocol] = []
