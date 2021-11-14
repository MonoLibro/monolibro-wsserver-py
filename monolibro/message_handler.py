from typing import Callable, Awaitable

MessageHandler = Callable[[], None]
AsyncMessageHandler = Callable[[], Awaitable]
