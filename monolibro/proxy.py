from typing import Dict, Union
import utils.base64
from .models import Message, User
from . import AsyncEventHandler, EventHandler, Intention
import websockets
import asyncio
import json


class Proxy:
    def __init__(self, ip: str, port: int, logger) -> None:
        self.ip = ip
        self.port = port

        self.logger = logger

        self.users = {}

        self.async_handlers: Dict[Intention, AsyncEventHandler] = {}
        self.handlers: Dict[Intention, EventHandler] = {}

    def join(self, connection, user_id):
        if not (user_id in self.users):
            self.users[user_id] = User(user_id)
        self.users[user_id].join(connection)

    def leave(self, connection, user_id):
        self.users[user_id].leave(connection)
        if self.users[user_id].is_empty():
            del self.users[user_id]

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
                raw_message_slices = (await ws.recv()).split(".")
                if len(raw_message_slices) != 2:
                    return

                decoded_raw_message_slices = [
                    utils.base64.decode_base64_url_no_padding(msg_slice).decode("utf_8")
                    for msg_slice in raw_message_slices
                ]

                message = Message(json.loads(decoded_raw_message_slices[0]))
                intention = message.details["intention"]
                if intention in self.handlers:
                    self.handlers[intention]()
                if intention in self.async_handlers:
                    await self.async_handlers[intention]()

                signature = decoded_raw_message_slices[1]

        return internal_handler

    async def start(self) -> None:
        self.logger.info(f"Listening on ws://{self.ip}:{self.port}")
        async with websockets.serve(self._get_internal_handlers(), self.ip, self.port):
            await asyncio.Future()
