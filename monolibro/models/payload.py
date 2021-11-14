from typing import Any

from pydantic import BaseModel

from .details import Details


class Payload(BaseModel):
    version: int
    sessionID: str
    details: Details
    operation: str
    data: dict[str, Any]
