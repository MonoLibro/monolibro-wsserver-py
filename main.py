import asyncio
from controls.websocket_server import WebSocketServer

wss = WebSocketServer("localhost", 3200)

asyncio.run(wss.start())
