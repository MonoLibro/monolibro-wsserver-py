from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey, RSAPrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat, PrivateFormat, NoEncryption, \
    BestAvailableEncryption


def dumps_rsa_public_key(public_key: RSAPublicKey) -> bytes:
    return public_key.public_bytes(
        encoding=Encoding.DER,
        format=PublicFormat.SubjectPublicKeyInfo
    )


def dumps_rsa_private_key(private_key: RSAPrivateKey, password: bytes = None) -> bytes:
    return private_key.private_bytes(
        encoding=Encoding.PEM,
        format=PrivateFormat.PKCS8,
        encryption_algorithm=NoEncryption() if not password else BestAvailableEncryption(password)
    )


def dumps_rsa_key_pair(
        public_key: RSAPublicKey,
        private_key: RSAPrivateKey, private_key_password: bytes = None
) -> (bytes, bytes):
    return dumps_rsa_public_key(public_key), dumps_rsa_private_key(private_key, private_key_password)


class RSAPublicKeyDERLoadError(Exception):
    pass


class RSAPrivateKeyDERLoadError(Exception):
    pass


def loads_rsa_public_key(der: bytes) -> RSAPublicKey:
    public_key = serialization.load_der_public_key(der)
    if not isinstance(public_key, RSAPublicKey):
        raise RSAPublicKeyDERLoadError("invalid RSA public key DER")
    return public_key


def loads_rsa_private_key(pem: bytes, password: str = None) -> RSAPrivateKey:
    private_key = serialization.load_der_private_key(pem, password)
    if not isinstance(private_key, RSAPrivateKey):
        raise RSAPrivateKeyDERLoadError("invalid RSA private key DER")
    return private_key
