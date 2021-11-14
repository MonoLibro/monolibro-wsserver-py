import os
from pathlib import Path


def dir_exists(path):
    return os.path.isdir(path)


def mkdirs(path):
    Path(path).mkdir(parents=True, exist_ok=True)
