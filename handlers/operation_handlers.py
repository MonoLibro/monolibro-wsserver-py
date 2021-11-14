from loguru import logger

from monolibro.models import Operation

def register(handler):
    logger.info("Registering operations")
    
    @handler.handler(Operation.JOIN_NETWORK)
    def join_network(ws, proxy, payload, signature):
        print("If you ever see this message being written to stdout, this marks the milestone of human civilization development, and a step foward to world peace.")

    logger.info("Operations registered")