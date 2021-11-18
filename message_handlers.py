import asyncio

from loguru import logger
from websockets.legacy.server import WebSocketServerProtocol
from cryptography.hazmat.primitives import hashes

from monolibro import ProxyState
from database import database
from monolibro import VotingSession
from monolibro.models import Intention, Operation, User, Payload


def register_to_proxy(proxy):
    logger.info("Registering handlers")

    @proxy.handler(Intention.BROADCAST, Operation.FREEZE_ACCOUNT)
    @proxy.handler(Intention.BROADCAST, Operation.UPDATE_ACCOUNT)
    @proxy.handler(Intention.BROADCAST, Operation.JOIN_ACTIVITY)
    async def on_general_broadcast_fowarding(ws: WebSocketServerProtocol, state: ProxyState, payload: Payload, signature: bytes, raw_message: str):
        logger.debug(f"Broadcasting message | {payload.sessionID}")
        users = state.users
        for user in users:
            clients = users[user].clients
            for client in clients:
                await client.send(raw_message)

    @proxy.handler(Intention.SYSTEM, Operation.JOIN_NETWORK)
    async def on_system_join_network(ws: WebSocketServerProtocol, state: ProxyState, payload: Payload, signature: bytes, raw_message: str):
        logger.debug(f"Handling Intention: System | {payload.sessionID}")

        data = payload.data
        if "userID" not in data:
            logger.info("A client trys to join the network but rejected: Insufficient payload data")
            await ws.close()
            return
        user_id = data["userID"]
        if user_id not in state.users:
            state.users[user_id] = User(id=user_id)
        if ws not in state.users[user_id].clients:
            state.users[user_id].clients.append(ws)
            logger.info(f"A client of {user_id} has joined the network.")
        else:
            logger.warning(f"A client of {user_id} trys to join the network while already being in the network. "
                           f"Ignoring.")
        logger.debug(f"The id of the ws object is {id(ws)}")

    @proxy.handler(Intention.BROADCAST, Operation.VOTE_SESSION_QUERY)
    async def on_broadcast_vote_session_query(ws: WebSocketServerProtocol, state: ProxyState, payload: Payload, signature: bytes, raw_message: str):
        compulsory_fields=["userID", "votingSessionID", "votingValue"]
        for field in compulsory_fields:
            if field not in payload.data:
                logger.warning("A client trys to vote with invalid payload data. Ignoring | {payload.sessionID}")
                return
        
        user_id = payload.data["userID"]
        voting_session_id = payload.data["votingSessionID"]
        voting_value = payload.data["votingValue"]

        if voting_session_id not in state.votes:
            logger.warning("A client trys to vote to non-exist voting session. Ignoring | {payload.sessionID}")
            return

        voting_session = state.votes[voting_session_id]

        logger.debug(f"Announcing vote | {payload.sessionID}")

        for user_id in voting_session.voting_context["users"].keys():
            user = voting_session.voting_context["users"][user_id]
            for connection in user.clients:
                await connection.send(raw_message)

        voting_session.vote(user_id, voting_value)

    @proxy.handler(Intention.BROADCAST, Operation.FREEZE_ACCOUNT)
    async def on_broadcast_freeze_account(ws: WebSocketServerProtocol, state: ProxyState, payload: Payload, signature: bytes, raw_message: str):
        compulsory_fields=["userID"]
        for field in compulsory_fields:
            if field not in payload.data:
                logger.warning("A client trys to freeze an account with invalid payload data. Ignoring | {payload.sessionID}")
                return
        user_id = payload.data["userID"]
        user_record = database["Users"][user_id][0]
        user_record[5] = 1
        user_record = database["Users"][user_id] = user_record
        database.commit()

    @proxy.handler(Intention.BROADCAST, Operation.CREATE_ACCUONT_INIT)
    async def on_broadcast_create_account_init(ws: WebSocketServerProtocol, state: ProxyState, payload: Payload, signature: bytes, raw_message: str):
        compulsory_fields=["userID", "firstName", "lastName", "email", "publicKey", "timestamp"]
        for field in compulsory_fields:
            if field not in payload.data:
                logger.warning("A client trys to create an account with invalid payload data. Ignoring | {payload.sessionID}")
                return
        voting_id = payload.data["userID"] + payload.data["timestamp"]
        digest = hashes.Hash(hashes.SHA256())
        digest.update(voting_id.encode())
        hashed_voting_id = digest.finalize().hex().upper()

        def fail_callback(session: VotingSession):
            del state.votes[hashed_voting_id]
            pass
        def success_callback(session: VotingSession):
            del state.votes[hashed_voting_id]
            database["Users"].insert([
                payload.data["userID"],
                payload.data["firstName"],
                payload.data["lastName"],
                payload.data["email"],
                payload.data["publicKey"],
                0,
            ])
            database.commit()
        def vote_callback(session: VotingSession):
            pass

        voting_session = VotingSession(hashed_voting_id, {"users":state.users},timeout=10 , fail_callback=fail_callback, vote_callback=vote_callback, success_callback=success_callback)
        state.votes[hashed_voting_id] = voting_session
        voting_session.start_voting()

        await on_general_broadcast_fowarding(ws, state, payload, signature, raw_message)

    logger.info("Handlers registered")