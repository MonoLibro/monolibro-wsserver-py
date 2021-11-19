from websockets.legacy.server import WebSocketServerProtocol

from .models import Payload
from .proxy_state import ProxyState


class Context:
    def __init__(self, ws: WebSocketServerProtocol, state: ProxyState, payload: Payload):
        self.ws = ws
        self.state = state
        self.payload = payload
