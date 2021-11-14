from loguru import logger

from monolibro.models.user import User
from monolibro.models import Operation


def register(handler):
    logger.info("Registering operations")

    @handler.handler(Operation.JOIN_NETWORK)
    async def join_network(ws, proxy, payload, signature):
        data = payload.data
        if "userID" not in data:
            logger.info("A client trys to join the network but rejected: Insufficient payload data")
            await ws.close()
            return
        user_id = data["userID"]
        logger.info(f"A client has joined the network with user of {user_id}")
        if user_id not in proxy.users:
            proxy.users[user_id] = User(id=user_id)
        proxy.users[user_id].clients.append(ws)


    logger.info("Operations registered")
