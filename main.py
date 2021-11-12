import asyncio
from controls.websocket_server import WebSocketServer

web_socket_server = WebSocketServer("localhost", 3200)

async def main():
    await web_socket_server.start()

asyncio.run(main())
