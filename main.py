import asyncio
import websockets


async def handler(ws, path):
    pass


async def main():
    async with websockets.serve(handler, "127.0.0.1", 3200):
        await asyncio.Future()


asyncio.run(main())
