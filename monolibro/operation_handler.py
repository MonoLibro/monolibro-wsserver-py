import asyncio
from typing import Union

from loguru import logger

from .message_handler import AsyncMessageHandler, MessageHandler
from .models.operation import Operation


class OperationHandler:
    def __init__(self):
        self.async_handlers: dict[Operation, list[AsyncMessageHandler]] = {}
        self.handlers: dict[Operation, list[MessageHandler]] = {}

    def handler(self, operation: Operation):
        def wrapper(func: Union[MessageHandler, AsyncMessageHandler]):
            if asyncio.iscoroutinefunction(func):
                if operation.value not in self.async_handlers:
                    self.async_handlers[operation.value] = []
                self.async_handlers[operation.value].append(func)
            else:
                if operation.value not in self.handlers:
                    self.handlers[operation.value] = []
                self.handlers[operation.value].append(func)
            
            return func

        return wrapper
    

    async def handle(self, ws, proxy, payload, signature):
        operation = payload.operation.value
        if operation in self.async_handlers:
            logger.debug(f"Handling async operation | {payload.sessionID}")
            for handler in self.async_handlers[operation]:
                logger.debug(f"Awaiting async operation handler#{id(handler)} | {payload.sessionID}")
                await handler(ws, proxy, payload, signature)
        if operation in self.handlers:
            logger.debug(f"Handling operation | {payload.sessionID}")
            for handler in self.handlers[operation]:
                logger.debug(f"Calling operation handler#{id(handler)} | {payload.sessionID}")
                handler(ws, proxy, payload, signature)