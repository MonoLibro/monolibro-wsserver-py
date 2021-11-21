from pydantic import BaseModel


class FreezeAccountData(BaseModel):
    userID: str
