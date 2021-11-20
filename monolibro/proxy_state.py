from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey, RSAPrivateKey

from database import Database
from .models import User
from .voting_session import VotingSession


class ProxyState:
    def __init__(self, database: Database, public_key: RSAPublicKey, private_key: RSAPrivateKey) -> None:
        self.database = database

        self.public_key = public_key
        self.private_key = private_key

        self.users: dict[str, User] = {}
        self.votes: dict[str, VotingSession] = {}
