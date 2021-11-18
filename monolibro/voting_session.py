import asyncio
from typing import Callable, Dict

from loguru import logger


class VotingSession:
    voting_id: str
    voting_context: Dict[str, any]
    results: Dict[str, bool]
    timeout: int
    success_callback: Callable[[], None]
    fail_callback: Callable[[], None]
    vote_callback: Callable[[], None]
    status: int
    def __init__(
        self,
        voting_id: str, # Key for quering the voting session
        voting_context: Dict[str, any], # Participation
        timeout: int = 10, # Timeout in sec
        success_callback: Callable[[], None] = None, # Callback function when voting has done
        fail_callback: Callable[[], None] = None, # Callback function when voting has timeouted
        vote_callback: Callable[[], None] = None # Callback function when voting has timeouted
    ):

        if "users" not in voting_context:
            # Exception to be converted to custom exception
            raise Exception("Insufficient members in voting context")

        self.voting_id = voting_id
        self.results = {}
        self.timeout = timeout
        self.success_callback = success_callback
        self.fail_callback = fail_callback
        self.vote_callback = vote_callback

        # To be converted to data class
        self.voting_context = voting_context
        # To be converted to enum. 0 = pre-voting, 1 = voting, 2 = post-voting
        self.status = 0
    
    def get_total_user_count(self) -> int:
        users = self.voting_context["users"]
        return len(users)
    
    def is_user_in_context(self, user_id: str) -> bool:
        users = self.voting_context["users"]
        return user_id in users

    def vote(self, user_id: str, vote: bool) -> None:
        # If statement condiciton to be converted to enum
        if self.status != 1:
            # Exception to be converted to custom exception
            raise Exception("Voting is not allowed in this status")
        elif not self.is_user_in_context(user_id):
            # Exception to be converted to custom exception
            raise Exception("User not in voting context")
        else:
            self.results[user_id] = vote
        
        logger.debug(f"Voting Session {self.voting_id} has someone voted")
        self.vote_callback(self)
        
        if self.has_vote_passed():
            logger.debug(f"Voting Session {self.voting_id} has successfuly passed")
            self.success_callback(self)
            self.status = 2

    def has_vote_passed(self) -> bool:
        return self.get_assent_votes() >= int((self.get_total_user_count() + 1) / 2)

    def get_voted_user_count(self) -> int:
        return len(self.results)
    
    def get_assent_votes(self) -> int:
        count = 0
        for user_id in self.results:
            if self.results[user_id]:
                count += 1
        return count

    async def wait_for_votes(self):
        self.status = 1
        await asyncio.sleep(self.timeout)
        if self.status == 1:
            logger.debug(f"Voting Session {self.voting_id} has timed-out")
            if self.has_vote_passed():
                self.success_callback(self)
            else:
                self.fail_callback(self)
            self.status = 2

    def start_voting(self):
        logger.debug(f"Voting session {self.voting_id} has started with a timeout of {self.timeout}")
        asyncio.create_task(self.wait_for_votes())