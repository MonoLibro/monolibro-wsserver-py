from typing import Any

from pydantic import BaseModel

from .details import Details
from .operation import Operation


class Payload(BaseModel):
    version: int
    sessionID: str
    details: Details
    operation: Operation
    data: dict[str, Any]
