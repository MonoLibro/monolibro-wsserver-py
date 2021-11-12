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
        async with websockets.serve(self.on_message(), self.ip, self.port):
            await asyncio.Future()

    def handler(self, name):
        def wrapper(func):
            self.handlers[name] = func
            return func
        return wrapper