import asyncio
import sys

import click
from loguru import logger

import handlers
import monolibro
import utils
from config import Config

default_config = Config()


@click.command()
@click.option("-c", "--config", "config_path", type=str, default="config.json", help="Configuration file path.")
@click.option("-d", "--debug", default=False, type=bool, help="Debug mode.", is_flag=True)
@logger.catch()
def main(config_path: str, debug: bool):
    # setup logger
    logger.remove()
    logger.add(sys.stdout, level="DEBUG" if debug else "INFO")

    # create config
    config = utils.config.create_if_not_exists(config_path, default_config)

    # generate key pair
    utils.rsa.generate_key_pair_pem_if_not_exists(config.public_key_path, config.private_key_path)

    # register operation handlers
    operation_handler = monolibro.OperationHandler()
    handlers.register_operations(operation_handler)

    # create proxy and register intention handlers
    wss = monolibro.Proxy(config.host, config.port, operation_handler)
    handlers.register_intentions(wss)

    # start proxy
    asyncio.run(wss.start())


if __name__ == "__main__":
    main()
