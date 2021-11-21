from pydantic import BaseModel


class VoteSessionQueryData(BaseModel):
    userID: str
    votingSessionID: str
    votingValue: bool
