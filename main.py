import asyncio
import ws

wss = ws.Server("localhost", 3200)

asyncio.run(wss.start())
