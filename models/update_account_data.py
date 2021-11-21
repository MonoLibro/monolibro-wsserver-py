from pydantic import BaseModel


class UpdateAccountData(BaseModel):
    userID: str
    firstName: str
    lastName: str
    email: str
