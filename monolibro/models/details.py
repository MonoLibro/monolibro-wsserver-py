from pydantic import BaseModel

from monolibro import Intention


class Details(BaseModel):
    intention: Intention
    target: str
