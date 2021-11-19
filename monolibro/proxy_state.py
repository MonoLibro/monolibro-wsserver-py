from .models import User
from .voting_session import VotingSession


class ProxyState:
    def __init__(self) -> None:
        self.users: dict[str, User] = {}
        self.votes: dict[str, VotingSession] = {}
