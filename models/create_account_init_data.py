import datetime

from pydantic import BaseModel


class CreateAccountInitData(BaseModel):
    userID: str

    firstName: str
    lastName: str

    email: str

    publicKey: str

    timestamp: datetime.datetime
