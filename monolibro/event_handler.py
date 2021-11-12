from typing import Callable, Awaitable

EventHandler = Callable[[], None]
AsyncEventHandler = Callable[[], Awaitable]
