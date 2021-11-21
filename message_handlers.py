from cryptography.hazmat.primitives import hashes
from loguru import logger
from pydantic import ValidationError

from models import CreateAccountInitData, JoinNetworkData, VoteSessionQueryData, UpdateAccountData, FreezeAccountData
from monolibro import VotingSession, Context
from monolibro.models import Intention, Operation, User


def register_to_proxy(proxy):
    logger.info("Registering handlers")

    @proxy.handler(Intention.BROADCAST, Operation.FREEZE_ACCOUNT)
    @proxy.handler(Intention.BROADCAST, Operation.UPDATE_ACCOUNT)
    @proxy.handler(Intention.BROADCAST, Operation.JOIN_ACTIVITY)
    @proxy.handler(Intention.BROADCAST, Operation.UPDATE_ACTIVITY)
    @proxy.handler(Intention.BROADCAST, Operation.SIGN_ACTIVITY)
    @proxy.handler(Intention.BROADCAST, Operation.LEAVE_ACTIVITY)
    @proxy.handler(Intention.BROADCAST, Operation.COMMIT_ACTIVITY)
    @proxy.handler(Intention.BROADCAST, Operation.CLEAR_PAYMENT_INIT)
    @proxy.handler(Intention.BROADCAST, Operation.CLEAR_PAYMENT_CONFIRM)
    async def on_general_broadcast_forwarding(ctx: Context):
        logger.debug(f"Broadcasting message | {ctx.payload.sessionID}")
        users = ctx.state.users
        for user in users:
            clients = users[user].clients
            for client in clients:
                await client.send(ctx.payload.json())

    @proxy.handler(Intention.SYSTEM, Operation.JOIN_NETWORK)
    async def on_system_join_network(ctx: Context):
        logger.debug(f"Handling Intention: System | {ctx.payload.sessionID}")

        try:
            data = JoinNetworkData(**ctx.payload.data)
        except ValidationError:
            logger.info("A client trys to join the network but rejected: Insufficient payload data")
            await ctx.ws.close()
            return

        user_id = data.userID
        if user_id not in ctx.state.users:
            ctx.state.users[user_id] = User(id=user_id)
        if ctx.ws not in ctx.state.users[user_id].clients:
            ctx.state.users[user_id].clients.append(ctx.ws)
            logger.info(f"A client of {user_id} has joined the network.")
        else:
            logger.warning(f"A client of {user_id} trys to join the network while already being in the network. "
                           f"Ignoring.")
        logger.debug(f"The id of the ws object is {id(ctx.ws)}")

    @proxy.handler(Intention.BROADCAST, Operation.VOTE_SESSION_QUERY)
    async def on_broadcast_vote_session_query(ctx: Context):
        try:
            data = VoteSessionQueryData(**ctx.payload.data)
        except ValidationError:
            logger.warning("A client trys to vote with invalid payload data. Ignoring | {payload.sessionID}")
            return

        user_id = data.userID
        voting_session_id = data.votingSessionID
        voting_value = data.votingValue

        if voting_session_id not in ctx.state.votes:
            logger.warning("A client trys to vote to non-exist voting session. Ignoring | {payload.sessionID}")
            return

        voting_session = ctx.state.votes[voting_session_id]

        logger.debug(f"Announcing vote | {ctx.payload.sessionID}")

        for user_id in voting_session.voting_context["users"].keys():
            user = voting_session.voting_context["users"][user_id]
            for connection in user.clients:
                await connection.send(ctx.payload.json())

        voting_session.vote(user_id, voting_value)

    @proxy.handler(Intention.BROADCAST, Operation.UPDATE_ACCOUNT)
    async def on_broadcast_update_account(ctx: Context):
        try:
            data = UpdateAccountData(**ctx.payload.data)
        except ValidationError:
            logger.warning(
                "A client trys to update an account with invalid payload data. Ignoring | {payload.sessionID}")
            return

        user_id = data.userID
        first_name = data.firstName
        last_name = data.lastName
        email = data.email

        user_record = ctx.state.database["Users"][user_id][0]
        user_record[1] = first_name
        user_record[2] = last_name
        user_record[3] = email
        ctx.state.database["Users"][user_id] = user_record
        ctx.state.database.commit()

    @proxy.handler(Intention.BROADCAST, Operation.FREEZE_ACCOUNT)
    async def on_broadcast_freeze_account(ctx: Context):
        try:
            data = FreezeAccountData(**ctx.payload.data)
        except ValidationError:
            logger.warning(
                "A client trys to freeze an account with invalid payload data. Ignoring | {payload.sessionID}")
            return

        user_id = data.userID
        user_record = ctx.state.database["Users"][user_id][0]
        user_record[5] = 1
        ctx.state.database["Users"][user_id] = user_record
        ctx.state.database.commit()

    @proxy.handler(Intention.BROADCAST, Operation.CREATE_ACCOUNT_INIT)
    async def on_broadcast_create_account_init(ctx: Context):
        try:
            data = CreateAccountInitData(**ctx.payload.data)
        except ValidationError:
            logger.warning(
                "A client trys to create an account with invalid payload data. Ignoring | {payload.sessionID}")
            return

        voting_id = data.userID + str(int(data.timestamp.timestamp()))
        digest = hashes.Hash(hashes.SHA256())
        digest.update(voting_id.encode())
        hashed_voting_id = digest.finalize().hex().upper()

        def fail_callback(session: VotingSession):
            del ctx.state.votes[hashed_voting_id]
            pass

        def success_callback(session: VotingSession):
            del ctx.state.votes[hashed_voting_id]
            ctx.state.database["Users"].insert([
                data.userID,
                data.firstName,
                data.lastName,
                data.email,
                data.publicKey,
                0,
            ])
            ctx.state.database.commit()

        def vote_callback(session: VotingSession):
            pass

        voting_session = VotingSession(hashed_voting_id, {"users": ctx.state.users}, timeout=10,
                                       fail_callback=fail_callback, vote_callback=vote_callback,
                                       success_callback=success_callback)
        ctx.state.votes[hashed_voting_id] = voting_session
        voting_session.start_voting()

        await on_general_broadcast_forwarding(ctx)

    logger.info("Handlers registered")
