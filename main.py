import asyncio
import ws

wss = ws.Server("localhost", 3200)

if __name__ == "__main__":
    asyncio.run(wss.start())
