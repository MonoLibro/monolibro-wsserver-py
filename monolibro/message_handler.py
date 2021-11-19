from typing import Callable, Awaitable

from .context import Context

MessageHandler = Callable[[Context], None]
AsyncMessageHandler = Callable[[Context], Awaitable]
