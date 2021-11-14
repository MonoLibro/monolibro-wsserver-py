from pydantic import BaseModel

from .intention import Intention


class Details(BaseModel):
    intention: Intention
    target: str
