from loguru import logger
from websockets.legacy.server import WebSocketServerProtocol

from monolibro import ProxyState
from monolibro.models import Intention, Operation, User, Payload


def register_to_proxy(proxy):
    logger.info("Registering handlers")

    # @proxy.handler(Intention.BROADCAST)
    # async def broadcast(ws, proxy, payload, signature):
    #     await proxy.operation_handler.handle(ws, proxy, payload, signature)
    #
    # @proxy.handler(Intention.SPECIFIC)
    # async def specific(ws, proxy, payload, signature):
    #     await proxy.operation_handler.handle(ws, proxy, payload, signature)

    @proxy.handler(Intention.SYSTEM, Operation.JOIN_NETWORK)
    async def on_system_join_network(ws: WebSocketServerProtocol, state: ProxyState, payload: Payload, signature: bytes, raw_message: str):
        logger.debug(f"Handling Intention: System | {payload.sessionID}")

        data = payload.data
        if "userID" not in data:
            logger.info("A client trys to join the network but rejected: Insufficient payload data")
            await ws.close()
            return
        user_id = data["userID"]
        if user_id not in state.users:
            state.users[user_id] = User(id=user_id)
        if ws not in state.users[user_id].clients:
            state.users[user_id].clients.append(ws)
            logger.info(f"A client of {user_id} has joined the network.")
        else:
            logger.warning(f"A client of {user_id} trys to join the network while already being in the network. "
                           f"Ignoring.")
        logger.debug(f"The id of the ws object is {id(ws)}")

    logger.info("Handlers registered")
