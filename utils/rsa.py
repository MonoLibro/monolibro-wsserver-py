from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey, RSAPrivateKey


def generate_key_pair(key_size: int, public_exponent: int = 65537) -> (RSAPublicKey, RSAPrivateKey):
    private_key = rsa.generate_private_key(public_exponent, key_size)
    return private_key.public_key(), private_key
