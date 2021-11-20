from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey, RSAPrivateKey

from .models import User
from .voting_session import VotingSession


class ProxyState:
    def __init__(self, public_key: RSAPublicKey, private_key: RSAPrivateKey) -> None:
        self.public_key = public_key
        self.private_key = private_key

        self.users: dict[str, User] = {}
        self.votes: dict[str, VotingSession] = {}
