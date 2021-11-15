import json
import os

from config import Config


def create(path: str, config_obj: Config) -> None:
    with open(path, "w") as file:
        json.dump(config_obj.__dict__, file, indent=2)


def load(path: str) -> Config:
    with open(path, "r") as file:
        return Config(**json.load(file))


def create_if_not_exists(path: str, default: Config) -> (Config, bool):
    if os.path.isfile(path):
        return load(path), False
    else:
        create(path, default)
        return default, True
