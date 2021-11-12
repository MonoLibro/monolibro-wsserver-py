import asyncio
import monolibro

wss = monolibro.Proxy("localhost", 3200)

asyncio.run(wss.start())
