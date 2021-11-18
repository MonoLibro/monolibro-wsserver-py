import asyncio
from typing import Callable, Dict


class VotingSession:
    voting_control: any
    voting_id: str
    voting_context: Dict[str, any]
    results: Dict[str, bool]
    timeout: int
    success_callback: Callable[[], None]
    timeout_callback: Callable[[], None]
    vote_callback: Callable[[], None]
    status: int
    def __init__(
        self,
        voting_control: any,
        voting_id: str, # Key for quering the voting session
        voting_context: Dict[str, any], # Participation
        timeout: int = 10, # Timeout in sec
        success_callback: Callable[[], None] = None, # Callback function when voting has done
        timeout_callback: Callable[[], None] = None, # Callback function when voting has timeouted
        vote_callback: Callable[[], None] = None # Callback function when voting has timeouted
    ):

        if "users" not in voting_context:
            # Exception to be converted to custom exception
            raise Exception("Insufficient members in voting context")

        self.voting_control = voting_control
        self.voting_id = voting_id
        self.results = {}
        self.timeout = timeout
        self.success_callback = success_callback
        self.timeout_callback = timeout_callback
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
        if self.vote_callback:
            self.vote_callback()
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
        
        if self.get_assent_votes >= int((self.get_total_user_count + 1) / 2):
            self.success_callback()

        self.vote_callback()

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
        self.status = 2
        self.timeout_callback()

    async def start_voting(self):
        await asyncio.create_task(self.wait_for_votes())