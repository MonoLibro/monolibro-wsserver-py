from typing import Callable, Awaitable, Any

from websockets.legacy.server import WebSocketServerProtocol

from .models import Payload

MessageHandler = Callable[[WebSocketServerProtocol, Any, Payload, bytes], None]
AsyncMessageHandler = Callable[[WebSocketServerProtocol, Any, Payload, bytes], Awaitable]
