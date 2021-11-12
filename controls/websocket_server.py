import websockets
import asyncio

class WebSocketServer:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.handlers = {}
    
    def on_message(self):
        async def raw_handler(ws, path):
            pass
        return raw_handler

    async def start(self):
        async with websockets.serve(self.on_message(), "127.0.0.1", 3200):
            await asyncio.Future()

    def handler(self, name):
        def wrapper(func):
            self.hanlders[name] = func
            return func
        return wrapper