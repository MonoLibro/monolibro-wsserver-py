import asyncio
import os.path
import sys

import click
from loguru import logger

import database
import message_handlers
import monolibro
import utils
from config import Config
from utils.pem import RSAPrivateKeyLoadError

default_config = Config()


@click.command()
@click.option("-c", "--config", "config_path",
              type=str, default="config.json",
              help="Configuration file path.")
@click.option("-d", "--debug",
              type=bool, default=False, is_flag=True,
              help="Debug mode.")
@click.option("-i", "--init-db", "init_database",
              type=bool, default=False, is_flag=True,
              help="Wipe and re-initialize database.")
@logger.catch()
def main(config_path: str, debug: bool, init_database: bool):
    # initialize database
    if init_database:
        logger.info(f"Wiping and re-initializing database . . .")
        database.database.force_reset()

    # setup logger
    logger.remove()
    logger.add(sys.stdout, level="DEBUG" if debug else "INFO")

    # create config
    logger.info("Checking configuration file . . .")
    config, config_created = utils.config.create_if_not_exists(config_path, default_config)
    if config_created:
        logger.info(f"Configuration file ({os.path.abspath(config_path)}) created")
    else:
        logger.info("Configuration file already exists, creation skipped")

    # generate key pair
    logger.info("Checking public and private key pair PEM files . . .")
    try:
        public_key, private_key, pem_created = utils.rsa.generate_key_pair_pem_if_not_exists(
            config.public_key_path, config.private_key_path)
        if not public_key and not private_key:
            return

        if pem_created:
            logger.info("Public and private key pair PEM files generated")
        else:
            logger.info("Public and private key pair PEM files already exist, generation skipped")
    except RSAPrivateKeyLoadError:
        logger.critical("Failed to load existing private key")

    # create proxy instance
    logger.info("Creating proxy instance")
    proxy = monolibro.Proxy(config.host, config.port)

    # register message handlers
    logger.info("Registering intention handlers")
    message_handlers.register_to_proxy(proxy)

    # start proxy
    logger.info("Starting proxy")
    asyncio.run(proxy.start())


if __name__ == "__main__":
    main()
