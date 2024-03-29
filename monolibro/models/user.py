from websockets.legacy.server import WebSocketServerProtocol


class User:
    def __init__(self, user_id: str, clients: list[WebSocketServerProtocol] = None):
        self.id = user_id
        self.clients = clients if clients else []
