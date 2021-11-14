from pydantic import BaseModel


class User(BaseModel):
    id: str
    clients: list = []
