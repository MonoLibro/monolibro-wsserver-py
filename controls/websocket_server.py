import websockets
import asyncio
import base64
import json

class WebSocketServer:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.handlers = {}
    
    def on_message(self):
        async def raw_handler(ws, path):
            while True:
                raw_messages = (await ws.recv()).split(".")
                decoded = [base64.b64decode(i + '=' * (4 - len(i) % 4)).decode() for i in raw_messages]
                signature = decoded[0]
                message = json.loads(decoded[1])
        return raw_handler

    async def start(self):
        print(f"listening on ws://{self.ip}:{self.port}")
        async with websockets.serve(self.on_message(), self.ip, self.port):
            await asyncio.Future()

    def handler(self, name):
        def wrapper(func):
            self.handlers[name] = func
            return func
        return wrapper