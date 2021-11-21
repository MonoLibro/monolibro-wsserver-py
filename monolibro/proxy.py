import asyncio
import base64
import json
from typing import Union

import websockets
import websockets.exceptions
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey, RSAPrivateKey
from loguru import logger
from websockets.legacy.server import WebSocketServerProtocol

import utils
from database import Database
from utils.message import DeserializePayloadError
from .context import Context
from .message_handler import AsyncMessageHandler, MessageHandler
from .models import Intention, Operation
from .proxy_state import ProxyState


class Proxy:
    def __init__(self, ip: str, port: int, database: Database, public_key: RSAPublicKey,
                 private_key: RSAPrivateKey) -> None:
        self.ip = ip
        self.port = port

        self.state = ProxyState(database, public_key, private_key)

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
        async def internal_handler(ws: WebSocketServerProtocol, path):
            logger.debug(f"#{id(ws)}: New connection from {ws.remote_address[0]}:{ws.remote_address[1]}")

            pub_key_der = utils.der.dumps_rsa_public_key(self.state.public_key)
            pub_key_der_encoded = base64.b64encode(pub_key_der).decode()
            await ws.send(json.dumps({
                "format": "DER",
                "encoding": "base64",
                "publicKey": pub_key_der_encoded
            }))

            while True:
                try:
                    message = await ws.recv()
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

                logger.debug(f"#{id(ws)}: Deserializing message")
                try:
                    payload = utils.message.deserialize(message, self.state.private_key)
                except DeserializePayloadError as e:
                    logger.debug(f"#{id(ws)}: Deserialize payload error: {e}")
                    continue

                intention = payload.details.intention
                operation = payload.operation
                handler_key = (intention, operation)
                if handler_key in self.handlers:
                    logger.debug(f"#{id(ws)}: Handling intention | {payload.sessionID}")
                    for handler in self.handlers[handler_key]:
                        logger.debug(f"#{id(ws)}: Calling intention handler#{id(handler)} | {payload.sessionID}")
                        handler(Context(ws, self.state, payload))
                if handler_key in self.async_handlers:
                    logger.debug(f"#{id(ws)}: Handling async intention | {payload.sessionID}")
                    for async_handler in self.async_handlers[handler_key]:
                        logger.debug(
                            f"#{id(ws)}: Awaiting async intention handler#{id(async_handler)} | {payload.sessionID}")
                        await async_handler(Context(ws, self.state, payload))

        return internal_handler

    async def start(self) -> None:
        logger.info(f"Proxy listening on ws://{self.ip}:{self.port}")
        async with websockets.serve(self._get_internal_handlers(), self.ip, self.port):
            await asyncio.Future()
