from typing import Any

from pydantic import BaseModel

from .operation import Operation
from .details import Details


class Payload(BaseModel):
    version: int
    sessionID: str
    details: Details
    operation: Operation
    data: dict[str, Any]
