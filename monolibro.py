import asyncio
import os.path

import click
from loguru import logger

import monolibro
import utils
from config import Config
from utils.pem import RSAPrivateKeyLoadError

default_config = Config()


@click.command()
@click.option("-c", "--config", "config_path", type=str, default="config.json", help="Configuration file path.")
@logger.catch()
def main(config_path: str):
    config = utils.config.create_if_not_exists(config_path, default_config)

    # if both public key and private key are not found,
    # generate new key pair and write directly
    #
    # if private key is found but public key is not found,
    # get public key from private and write directly
    #
    # if private key is not found but public key is found,
    # ask if user want to generate a new key pair and overwrite existing public key
    if not os.path.isfile(config.private_key_path):
        public_key_exists = os.path.isfile(config.public_key_path)

        if public_key_exists:
            should_gen_input = None
            while should_gen_input != "y" and should_gen_input != "n":
                should_gen_input = input(
                    "Missing private key, generate and overwrite existing public key? (y/n): ").lower()
            if should_gen_input.lower() == "n":
                return

        public_key, private_key = utils.rsa.generate_key_pair(2048)
        public_key_pem, private_key_pem = utils.pem.dumps_rsa_key_pair(public_key, private_key)

        if not utils.fs.dir_exists(os.path.dirname(config.public_key_path)):
            utils.fs.mkdirs(os.path.dirname(config.public_key_path))
        with open(config.public_key_path, "wb") as public_key_file:
            public_key_file.write(public_key_pem)

        if not utils.fs.dir_exists(os.path.dirname(config.private_key_path)):
            utils.fs.mkdirs(os.path.dirname(config.private_key_path))
        with open(config.private_key_path, "wb") as private_key_file:
            private_key_file.write(private_key_pem)
    elif os.path.isfile(config.private_key_path):
        with open(config.private_key_path, "rb") as private_key_file:
            try:
                private_key = utils.pem.loads_rsa_private_key(private_key_file.read())
            except RSAPrivateKeyLoadError as e:
                logger.critical(e)
                return

        public_key_pem = utils.pem.dumps_rsa_public_key(private_key.public_key())

        if not utils.fs.dir_exists(os.path.dirname(config.public_key_path)):
            utils.fs.mkdirs(os.path.dirname(config.public_key_path))
        with open(config.public_key_path, "wb") as public_key_file:
            public_key_file.write(public_key_pem)

    wss = monolibro.Proxy(config.host, config.port)
    asyncio.run(wss.start())


if __name__ == "__main__":
    main()
