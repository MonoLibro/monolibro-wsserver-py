from .models import User


class ProxyState:
    def __init__(self) -> None:
        self.users: dict[str, User] = {}
