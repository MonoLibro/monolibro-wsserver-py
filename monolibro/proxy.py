from typing import Dict, Union
from models.message import Message
from . import AsyncEventHandler, EventHandler, Intention
import websockets
import asyncio
import base64
import json


class Proxy:
    def __init__(self, ip: str, port: int) -> None:
        self.ip = ip
        self.port = port

        self.async_handlers: Dict[Intention, AsyncEventHandler] = {}
        self.handlers: Dict[Intention, EventHandler] = {}

    def handler(self, intention: Intention):
        def wrapper(func: Union[EventHandler, AsyncEventHandler]):
            if asyncio.iscoroutinefunction(func):
                self.async_handlers[intention.value] = func
            else:
                self.handlers[intention.value] = func

            return func

        return wrapper

    def _get_internal_handlers(self):
        async def internal_handler(ws, path):
            while True:
                raw_messages = (await ws.recv()).split(".")
                decoded = [base64.b64decode(i + '=' * (4 - len(i) % 4)).decode() for i in raw_messages]
                signature = decoded[1]
                message = Message(json.loads(decoded[0]))
                if (message.details["intention"] in self.handlers):
                    self.handlers[message.details["intention"]]()
                if (message.details["intention"] in self.async_handlers):
                    await (self.handlers[message.details["intention"]]())

        return internal_handler

    async def start(self) -> None:
        async with websockets.serve(self._get_internal_handlers(), self.ip, self.port):
            await asyncio.Future()
