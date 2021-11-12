import websockets
import asyncio


class Server:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

        self.async_handlers = {}
        self.handlers = {}

    def handler(self, name):
        def wrapper(func):
            if asyncio.iscoroutinefunction(func):
                self.async_handlers[name] = func
            else:
                self.handlers[name] = func

            return func

        return wrapper

    def _get_internal_handlers(self):
        async def internal_handler(ws, path):
            pass

        return internal_handler

    async def start(self):
        async with websockets.serve(self._get_internal_handlers(), self.ip, self.port):
            await asyncio.Future()
