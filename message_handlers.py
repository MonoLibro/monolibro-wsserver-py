from cryptography.hazmat.primitives import hashes
from loguru import logger

from database import database
from monolibro import Context
from monolibro import VotingSession
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

        data = ctx.payload.data
        if "userID" not in data:
            logger.info("A client trys to join the network but rejected: Insufficient payload data")
            await ctx.ws.close()
            return
        user_id = data["userID"]
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
        compulsory_fields = ["userID", "votingSessionID", "votingValue"]
        for field in compulsory_fields:
            if field not in ctx.payload.data:
                logger.warning("A client trys to vote with invalid payload data. Ignoring | {payload.sessionID}")
                return

        user_id = ctx.payload.data["userID"]
        voting_session_id = ctx.payload.data["votingSessionID"]
        voting_value = ctx.payload.data["votingValue"]

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
        compulsory_fields = ["userID", "firstName", "lastName", "email"]
        for field in compulsory_fields:
            if field not in ctx.payload.data:
                logger.warning(
                    "A client trys to update an account with invalid payload data. Ignoring | {payload.sessionID}")
                return

        user_id = ctx.payload.data["userID"]
        first_name = ctx.payload.data["firstName"]
        last_name = ctx.payload.data["lastName"]
        email = ctx.payload.data["email"]

        user_id = ctx.payload.data["userID"]
        user_record = database["Users"][user_id][0]
        user_record[1] = first_name
        user_record[2] = last_name
        user_record[3] = email
        user_record = database["Users"][user_id] = user_record
        database.commit()

    @proxy.handler(Intention.BROADCAST, Operation.FREEZE_ACCOUNT)
    async def on_broadcast_freeze_account(ctx: Context):
        compulsory_fields = ["userID"]
        for field in compulsory_fields:
            if field not in ctx.payload.data:
                logger.warning(
                    "A client trys to freeze an account with invalid payload data. Ignoring | {payload.sessionID}")
                return
        user_id = ctx.payload.data["userID"]
        user_record = database["Users"][user_id][0]
        user_record[5] = 1
        user_record = database["Users"][user_id] = user_record
        database.commit()

    @proxy.handler(Intention.BROADCAST, Operation.CREATE_ACCOUNT_INIT)
    async def on_broadcast_create_account_init(ctx: Context):
        compulsory_fields = ["userID", "firstName", "lastName", "email", "publicKey", "timestamp"]
        for field in compulsory_fields:
            if field not in ctx.payload.data:
                logger.warning(
                    "A client trys to create an account with invalid payload data. Ignoring | {payload.sessionID}")
                return
        voting_id = ctx.payload.data["userID"] + ctx.payload.data["timestamp"]
        digest = hashes.Hash(hashes.SHA256())
        digest.update(voting_id.encode())
        hashed_voting_id = digest.finalize().hex().upper()

        def fail_callback(session: VotingSession):
            del ctx.state.votes[hashed_voting_id]
            pass

        def success_callback(session: VotingSession):
            del ctx.state.votes[hashed_voting_id]
            database["Users"].insert([
                ctx.payload.data["userID"],
                ctx.payload.data["firstName"],
                ctx.payload.data["lastName"],
                ctx.payload.data["email"],
                ctx.payload.data["publicKey"],
                0,
            ])
            database.commit()

        def vote_callback(session: VotingSession):
            pass

        voting_session = VotingSession(hashed_voting_id, {"users": ctx.state.users}, timeout=10,
                                       fail_callback=fail_callback, vote_callback=vote_callback,
                                       success_callback=success_callback)
        ctx.state.votes[hashed_voting_id] = voting_session
        voting_session.start_voting()

        await on_general_broadcast_forwarding(ctx)

    logger.info("Handlers registered")
