from pydantic import BaseModel


class JoinNetworkData(BaseModel):
    userID: str
