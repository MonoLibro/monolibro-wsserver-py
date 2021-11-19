import asyncio
import json
from typing import Union

import websockets
import websockets.exceptions
from loguru import logger
from pydantic import ValidationError

import utils
from .message_handler import AsyncMessageHandler, MessageHandler
from .models import Intention, Operation
from .models import Payload
from .proxy_state import ProxyState


class Proxy:
    def __init__(self, ip: str, port: int) -> None:
        self.ip = ip
        self.port = port

        self.state = ProxyState()

        self.async_handlers: dict[(Intention, Operation), list[AsyncMessageHandler]] = {}
        self.handlers: dict[(Intention, Operation), list[MessageHandler]] = {}

    def remove_from_user(self, ws):
        for (user_id, user) in self.state.users.items():
            user_clients = user.clients
            if ws in user_clients:
                del user_clients[user_clients.index(ws)]
                if not user_clients:
                    del user
                return

    def handler(self, intention: Intention, operation: Operation):
        def wrapper(func: Union[MessageHandler, AsyncMessageHandler]):
            handler_key = (intention, operation)

            if asyncio.iscoroutinefunction(func):
                if handler_key not in self.async_handlers:
                    self.async_handlers[handler_key] = []
                self.async_handlers[handler_key].append(func)
            else:
                if handler_key not in self.handlers:
                    self.handlers[handler_key] = []
                self.handlers[handler_key].append(func)

            return func

        return wrapper

    def _get_internal_handlers(self):
        async def internal_handler(ws, path):
            logger.debug(f"#{id(ws)}: New connection from {ws.remote_address[0]}:{ws.remote_address[1]}")
            while True:
                try:
                    raw_message = await ws.recv()
                except websockets.exceptions.ConnectionClosedOK:
                    logger.info(f"#{id(ws)}: Connection closed")
                    logger.debug(f"#{id(ws)}: Cleaning up connection")
                    self.remove_from_user(ws)
                    return
                except websockets.exceptions.ConnectionClosedError as e:
                    logger.info(f"#{id(ws)}: Connection closed unexpectedly: {e}")
                    logger.debug(f"#{id(ws)}: Cleaning up connection")
                    self.remove_from_user(ws)
                    return

                logger.debug(f"#{id(ws)}: Parsing message")

                raw_message_slices = raw_message.split(".")
                if len(raw_message_slices) != 2:
                    logger.info(f"#{id(ws)}: Malformed message received: {raw_message}")
                    continue

                decoded_raw_message_slices = [
                    utils.base64.decode_url_no_padding(msg_slice)
                    for msg_slice in raw_message_slices
                ]

                try:
                    logger.debug(f"#{id(ws)}: Parsing payload")
                    payload = Payload(**json.loads(decoded_raw_message_slices[0]))
                except ValidationError as e:
                    logger.debug(f"#{id(ws)}: Payload validation error: {e.json()}")
                    continue
                except json.decoder.JSONDecodeError as e:
                    logger.debug(f"#{id(ws)}: Payload validation error (invalid JSON format): {e}")
                    continue

                signature = decoded_raw_message_slices[1]

                intention = payload.details.intention
                operation = payload.operation
                handler_key = (intention, operation)
                if handler_key in self.handlers:
                    logger.debug(f"#{id(ws)}: Handling intention | {payload.sessionID}")
                    for handler in self.handlers[handler_key]:
                        logger.debug(f"#{id(ws)}: Calling intention handler#{id(handler)} | {payload.sessionID}")
                        handler(ws, self.state, payload, signature, raw_message)
                if handler_key in self.async_handlers:
                    logger.debug(f"#{id(ws)}: Handling async intention | {payload.sessionID}")
                    for async_handler in self.async_handlers[handler_key]:
                        logger.debug(
                            f"#{id(ws)}: Awaiting async intention handler#{id(async_handler)} | {payload.sessionID}")
                        await async_handler(ws, self.state, payload, signature, raw_message)

        return internal_handler

    async def start(self) -> None:
        logger.info(f"Proxy listening on ws://{self.ip}:{self.port}")
        async with websockets.serve(self._get_internal_handlers(), self.ip, self.port):
            await asyncio.Future()
