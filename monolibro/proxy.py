import asyncio
import json
from logging import log
from typing import Union

import websockets
from loguru import logger
from pydantic import ValidationError

import utils
from .event_handler import AsyncEventHandler, EventHandler
from .intention import Intention
from .models import Payload, User


class Proxy:
    def __init__(self, ip: str, port: int) -> None:
        self.ip = ip
        self.port = port

        self.users: dict[str, User] = {}

        self.async_handlers: dict[Intention, list[AsyncEventHandler]] = {}
        self.handlers: dict[Intention, list[EventHandler]] = {}

    def join(self, connection, user_id):
        if user_id not in self.users:
            self.users[user_id] = User(id=user_id)
        # self.users[user_id].join(connection)

    def leave(self, connection, user_id):
        # self.users[user_id].leave(connection)
        # if self.users[user_id].is_empty():
        #     del self.users[user_id]
        del self.users[user_id]

    def handler(self, intention: Intention):
        def wrapper(func: Union[EventHandler, AsyncEventHandler]):
            if asyncio.iscoroutinefunction(func):
                if intention.value not in self.async_handlers:
                    self.async_handlers[intention.value] = []
                self.async_handlers[intention.value].append(func)
            else:
                if intention.value not in self.handlers:
                    self.handlers[intention.value] = []
                self.handlers[intention.value].append(func)

            return func

        return wrapper

    def _get_internal_handlers(self):
        async def internal_handler(ws, path):
            while True:
                raw_message_slices = (await ws.recv()).split(".")
                if len(raw_message_slices) != 2:
                    return

                decoded_raw_message_slices = [
                    utils.base64.decode_url_no_padding(msg_slice).decode("utf_8")
                    for msg_slice in raw_message_slices
                ]

                try:
                    logger.debug(f"Paring Message")
                    payload = Payload(**json.loads(decoded_raw_message_slices[0]))
                    signature = decoded_raw_message_slices[1]
                    intention = payload.details.intention.value
                    if intention in self.handlers:
                        for handler in self.handlers[intention]:
                            handler(ws, self, payload, signature)
                    if intention in self.async_handlers:
                        for async_handler in self.async_handlers[intention]:
                            await async_handler(ws, self, payload, signature)
                except ValidationError as e:
                    logger.debug(f"Velidation Error: {e.json()}")
                    return

        return internal_handler

    async def start(self) -> None:
        logger.info(f"Listening on ws://{self.ip}:{self.port}")
        async with websockets.serve(self._get_internal_handlers(), self.ip, self.port):
            await asyncio.Future()
