from typing import Dict, Union
from . import AsyncEventHandler, EventHandler, EventType
import websockets
import asyncio


class Proxy:
    def __init__(self, ip: str, port: int) -> None:
        self.ip = ip
        self.port = port

        self.async_handlers: Dict[EventType, AsyncEventHandler] = {}
        self.handlers: Dict[EventType, EventHandler] = {}

    def handler(self, event_type: EventType):
        def wrapper(func: Union[EventHandler, AsyncEventHandler]):
            if asyncio.iscoroutinefunction(func):
                self.async_handlers[event_type] = func
            else:
                self.handlers[event_type] = func

            return func

        return wrapper

    def _get_internal_handlers(self):
        async def internal_handler(ws, path):
            pass

        return internal_handler

    async def start(self) -> None:
        async with websockets.serve(self._get_internal_handlers(), self.ip, self.port):
            await asyncio.Future()
