from typing import Any

from pydantic import BaseModel



class Payload(BaseModel):
    version: int
    sessionID: str
    details: dict[str, Any]
    operation: str
    data: dict[str, Any]
