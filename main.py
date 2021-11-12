import asyncio
import monolibro

wss = monolibro.Proxy("localhost", 3200)

if __name__ == "__main__":
    asyncio.run(wss.start())
