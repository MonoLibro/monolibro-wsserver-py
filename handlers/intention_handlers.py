from monolibro.intention import Intention
from loguru import logger

def register(proxy):
    logger.info("Registering intentions")

    @proxy.handler(Intention.BROADCAST)
    def broadcast(ws, proxy, payload, signature):
        pass
    

    @proxy.handler(Intention.SPECIFIC)
    def specific(ws, proxy, payload, signature):
        pass

    @proxy.handler(Intention.SYSTEM)
    def system(ws, proxy, payload, signature):
        pass

    logger.info("Intentions registered")