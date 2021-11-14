import asyncio
import sys

import click
from loguru import logger

import monolibro
import handlers 

@click.command()
@click.option("-h", "--host", default="127.0.0.1", type=str, help="Proxy host address.")
@click.option("-p", "--port", default=3200, type=int, help="Proxy port.")
@click.option("-d", "--debug", default=False, type=bool, help="Debug mode.", is_flag=True)
def main(host, port, debug):
    if (debug):
        logger.remove()
        logger.add(sys.stdout, level="DEBUG")

    operation_handler = monolibro.OperationHandler()
    handlers.register_operations(operation_handler)

    wss = monolibro.Proxy(host, port, operation_handler)
    handlers.register_intentions(wss)
    
    asyncio.run(wss.start())

if __name__ == "__main__":
    main()
