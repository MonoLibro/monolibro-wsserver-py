from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey, RSAPrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat, PrivateFormat, NoEncryption, \
    BestAvailableEncryption


def dumps_rsa_public_key(public_key: RSAPublicKey) -> bytes:
    return public_key.public_bytes(
        encoding=Encoding.PEM,
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


class RSAPublicKeyPEMLoadError(Exception):
    pass


class RSAPrivateKeyPEMLoadError(Exception):
    pass


def loads_rsa_public_key(pem: bytes) -> RSAPublicKey:
    public_key = serialization.load_pem_public_key(pem)
    if not isinstance(public_key, RSAPublicKey):
        raise RSAPublicKeyPEMLoadError("invalid RSA public key PEM")
    return public_key


def loads_rsa_private_key(pem: bytes, password: str = None) -> RSAPrivateKey:
    private_key = serialization.load_pem_private_key(pem, password)
    if not isinstance(private_key, RSAPrivateKey):
        raise RSAPrivateKeyPEMLoadError("invalid RSA private key PEM")
    return private_key
