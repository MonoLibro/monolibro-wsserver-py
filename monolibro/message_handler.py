from typing import Callable, Awaitable

from websockets.legacy.server import WebSocketServerProtocol

from .models import Payload
from .proxy_state import ProxyState

MessageHandler = Callable[[WebSocketServerProtocol, ProxyState, Payload, bytes], None]
AsyncMessageHandler = Callable[[WebSocketServerProtocol, ProxyState, Payload, bytes], Awaitable]
