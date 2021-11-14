from loguru import logger

from monolibro.models import Intention


def register(proxy):
    logger.info("Registering intentions")

    @proxy.handler(Intention.BROADCAST)
    def broadcast(ws, proxy, payload, signature):
        pass

    @proxy.handler(Intention.SPECIFIC)
    def specific(ws, proxy, payload, signature):
        pass

    @proxy.handler(Intention.SYSTEM)
    async def system(ws, proxy, payload, signature):
        logger.debug(f"Handling Intention: System | {payload.sessionID}")
        await proxy.operation_handler.handle(ws, proxy, payload, signature)

    logger.info("Intentions registered")
