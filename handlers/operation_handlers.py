from loguru import logger

from monolibro.models import Operation
from monolibro.models.user import User


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
        if user_id not in proxy.users:
            proxy.users[user_id] = User(id=user_id)
        if ws not in proxy.users[user_id].clients:
            proxy.users[user_id].clients.append(ws)
            logger.info(f"A client of {user_id} has joined the network.")
        else:
            logger.warning(f"A client of {user_id} trys to join the network while already being in the network. "
                           f"Ignoring.")
        logger.debug(f"The id of the ws object is {id(ws)}")

    logger.info("Operations registered")
