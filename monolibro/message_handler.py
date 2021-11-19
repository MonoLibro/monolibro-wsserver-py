from typing import Callable, Awaitable

from . import Context

MessageHandler = Callable[[Context], None]
AsyncMessageHandler = Callable[[Context], Awaitable]
