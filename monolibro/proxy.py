import asyncio
import json
from typing import Union

import websockets
from loguru import logger
from pydantic import ValidationError

import utils
from . import OperationHandler
from .message_handler import AsyncMessageHandler, MessageHandler
from .models import Intention
from .models import Payload, User


class Proxy:
    def __init__(self, ip: str, port: int, operation_handler: OperationHandler) -> None:
        self.ip = ip
        self.port = port

        self.operation_handler = operation_handler

        self.users: dict[str, User] = {}

        self.async_handlers: dict[Intention, list[AsyncMessageHandler]] = {}
        self.handlers: dict[Intention, list[MessageHandler]] = {}

    def handler(self, intention: Intention):
        def wrapper(func: Union[MessageHandler, AsyncMessageHandler]):
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
                raw_message = await ws.recv()
                raw_message_slices = raw_message.split(".")
                if len(raw_message_slices) != 2:
                    logger.info(f"Malformed message recieved: {raw_message}")
                    return

                decoded_raw_message_slices = [
                    utils.base64.decode_url_no_padding(msg_slice)
                    for msg_slice in raw_message_slices
                ]

                try:
                    logger.debug(f"Parsing Message: {decoded_raw_message_slices[0]}")

                    payload = Payload(**json.loads(decoded_raw_message_slices[0]))

                    signature = decoded_raw_message_slices[1]

                    intention = payload.details.intention.value
                    if intention in self.handlers:
                        logger.debug(f"Handling intention | {payload.sessionID}")
                        for handler in self.handlers[intention]:
                            logger.debug(f"Calling intention handler#{id(handler)} | {payload.sessionID}")
                            handler(ws, self, payload, signature)
                    if intention in self.async_handlers:
                        logger.debug(f"Handling async intention | {payload.sessionID}")
                        for async_handler in self.async_handlers[intention]:
                            logger.debug(f"Awaiting async intention handler#{id(async_handler)} | {payload.sessionID}")
                            await async_handler(ws, self, payload, signature)
                except ValidationError as e:
                    logger.debug(f"Velidation Error: {e.json()}")
                    return

        return internal_handler

    async def start(self) -> None:
        logger.info(f"Listening on ws://{self.ip}:{self.port}")
        async with websockets.serve(self._get_internal_handlers(), self.ip, self.port):
            await asyncio.Future()
