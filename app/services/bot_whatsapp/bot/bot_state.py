from pprint import pprint
from ....db import collection_conversation_state
from ....models.bot import (
    Message, ConversationState
)
from ....schemas.socket import (
    MessageSocket, MessageType
)
from ....core.socket import manager
from typing import Literal
from datetime import datetime, UTC
from fastapi.encoders import jsonable_encoder

async def broadcast_state(
    phone_number: str, locked: bool
)-> bool:
    try:
        ws_message = MessageSocket(
            phone_number=phone_number,
            type=MessageType.STATUS_UPDATE,
            locked=locked,
            date=datetime.now(UTC)
        )
        await manager.broadcast(ws_message)
        print(f"Notificado estado de {phone_number}")
        return True
    except Exception as e:
        print(f"Error notificando estado de {phone_number}: {e}")
        return False

async def is_bot_locked(phone_number: str) -> bool:
    try:
        document = await collection_conversation_state.find_one(
            {"phone_number": phone_number}
        )

        if document is None:
            return False

        conversation_state = ConversationState(**document)
        return conversation_state.locked
    except Exception as e:
        print("Error: ", e)
        return False


async def unlock_bot(phone_number: str) -> None:
    await collection_conversation_state.update_one(
        {"phone_number": phone_number},
        {"$set": {"locked": False}},
        upsert=True,
    )

    await broadcast_state(phone_number, False)


async def lock_bot(phone_number: str) -> None:
    is_lock = await is_bot_locked(phone_number)
    if is_lock: # esto lo hago porque se envia envento y si ya esta bloquedado no quiero que se envie evento
        pprint("Bot ya esta bloqueado")
        return

    await collection_conversation_state.update_one(
        {"phone_number": phone_number},
        {"$set": {"locked": True}},
        upsert=True,  # This will create the document if it doesn't exist
    )

    await broadcast_state(phone_number, True)

async def update_message(
    phone_number: str, message: str, role: Literal["user", "assistant"]
) -> None:
    try:
        if not phone_number or not message:
            return

        document = await collection_conversation_state.find_one(
            {"phone_number": phone_number}
        )

        date_now = datetime.now(UTC)

        if document is None:
            conversation_state = ConversationState(
                phone_number=phone_number,
                messages=[Message(role=role, content=message, date=date_now)],
                date=date_now,
            )
        else:
            conversation_state = ConversationState(**document)
            if conversation_state.messages is None:
                conversation_state.messages = [Message(role=role, content=message, date=date_now)]
            else:
                conversation_state.messages.append(Message(role=role, content=message, date=date_now))
            conversation_state.date = date_now

        conversation_state_json = jsonable_encoder(conversation_state)

        await collection_conversation_state.update_one(
            {"phone_number": phone_number},
            {"$set": conversation_state_json},
            upsert=True,
        )
    except Exception as e:
        print("Error: ", e)