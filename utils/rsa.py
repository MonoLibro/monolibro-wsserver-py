import os
from types import Union

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey, RSAPrivateKey

from . import pem, fs, cli


def generate_key_pair(key_size: int, public_exponent: int = 65537) -> (RSAPublicKey, RSAPrivateKey):
    private_key = rsa.generate_private_key(public_exponent, key_size)
    return private_key.public_key(), private_key


def generate_key_pair_pem_if_not_exists(public_key_path, private_key_path) -> (
        Union[RSAPublicKey, None],
        Union[RSAPrivateKey, None],
        bool
):
    """
    Generate RSA key pair if it does not exist.

    If both public key and private key are not found, generate new key pair and write directly.

    If private key is found but public key is not found, get public key from private key and write directly.

    If private key is not found but public key is found,
    ask if the user wants to generate a new key pair and overwrite existing public key.
    """

    public_key_exists, private_key_exists = os.path.isfile(public_key_path), os.path.isfile(private_key_path)

    if private_key_exists:
        with open(private_key_path, "rb") as private_key_file:
            private_key = pem.loads_rsa_private_key(private_key_file.read())

        public_key = private_key.public_key()

        if public_key_exists:
            with open(public_key_path, "rb+") as public_key_file:
                if public_key_file.read() == pem.dumps_rsa_public_key(public_key):
                    return public_key, private_key, False
                else:
                    should_override_pub = cli.yn_question(
                        "Unmatched public and private key, generate and override existing public key?")
                    if not should_override_pub:
                        return None, None, False

                    public_key_file.truncate(0)
                    public_key_file.write(pem.dumps_rsa_public_key(public_key))

                    return public_key, private_key, False
        else:
            if not fs.dir_exists(os.path.dirname(public_key_path)):
                fs.mkdirs(os.path.dirname(public_key_path))
            with open(public_key_path, "wb") as public_key_file:
                public_key_file.write(pem.dumps_rsa_public_key(private_key.public_key()))

            return public_key, private_key, False
    else:
        if public_key_exists:
            should_gen = cli.yn_question("Missing private key, generate and overwrite existing public key?")
            if not should_gen:
                return None, None, False

        public_key, private_key = generate_key_pair(2048)
        public_key_pem, private_key_pem = pem.dumps_rsa_key_pair(public_key, private_key)

        if not fs.dir_exists(os.path.dirname(public_key_path)):
            fs.mkdirs(os.path.dirname(public_key_path))
        with open(public_key_path, "wb") as public_key_file:
            public_key_file.write(public_key_pem)

        if not fs.dir_exists(os.path.dirname(private_key_path)):
            fs.mkdirs(os.path.dirname(private_key_path))
        with open(private_key_path, "wb") as private_key_file:
            private_key_file.write(private_key_pem)

        return public_key, private_key, True
