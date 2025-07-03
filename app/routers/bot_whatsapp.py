from datetime import datetime
from fastapi import (
    APIRouter, 
    Request,
    Query,
    BackgroundTasks,
    Depends,
    HTTPException,
    status
)

from pprint import pprint

from ..schemas.bot_whatsapp import (
    ACKResponse, 
    MessageAi, 
    MessageUser, 
    WhatsappSendMessageRequest, 
    BotLockRequest,
)
from ..schemas.bot_whatsapp.event import WhatsappEvent
from ..schemas.bot_whatsapp import (
    Chats, Chat
)

from ..services.bot_whatsapp.ai.agent import agent
from ..services.bot_whatsapp.bot.bot_state import (
    lock_bot, unlock_bot
)
from ..services.bot_whatsapp.bot.process_event import (
    process_whatsapp_event, process_whatsapp_message
)
from ..db import collection_conversation_state
from ..core.security import validate_api_key

router = APIRouter(
    tags=["Bot-WhatsApp"],
)


# ================================================
# Handle whatsapp webhook events
# ================================================

@router.get("/webhook/whatsapp")
async def subscribe_to_webhook_events(
    hub_challenge: str | None = Query(None, alias="hub.challenge"),
):
    print("hub.challenge", hub_challenge)
    return hub_challenge


@router.post("/webhook/whatsapp")
async def receive_webhook_events(
    request: Request, background_tasks: BackgroundTasks
) -> ACKResponse:
    print("================================")
    print("Received whatsapp event")
    print("================================")
    body = await request.json()
    pprint(body)
    print("================================")
    event = WhatsappEvent(**body)

    if event.status:
        print("================================")
        print("Received status event")
        print(event.status)
        print("================================")
        return ACKResponse(message="Status event received")

    if not event.phone_number:
        return ACKResponse(message="Phone number not found")

    background_tasks.add_task(process_whatsapp_event, event)

    return ACKResponse(message="Message received")


# ================================================
# Handle whatsapp send message
# ================================================

@router.post("/webhook/whatsapp/send-message")
async def whatsapp_send_message(
    body: WhatsappSendMessageRequest,
    background_tasks: BackgroundTasks,
    _: str = Depends(validate_api_key),
) -> ACKResponse:

    background_tasks.add_task(process_whatsapp_message, body)
    
    return ACKResponse(message="Send Message")

# ================================================
# Handle whatsapp bot lock and unlock
# ================================================


@router.put("/webhook/whatsapp/lock")
async def lock_whastapp_bot(
    body: BotLockRequest, _: str = Depends(validate_api_key)
) -> ACKResponse:
    await lock_bot(body.phone_number)
    return ACKResponse(message="Bot locked")


@router.put("/webhook/whatsapp/unlock")
async def unlock_whastapp_bot(
    body: BotLockRequest, _: str = Depends(validate_api_key)
) -> ACKResponse:
    await unlock_bot(body.phone_number)
    return ACKResponse(message="Bot unlocked")


# ================================================
# Handle whatsapp ai message
# ================================================

@router.post("/bot-whatsapp/message/", response_model=MessageAi)
async def get_message_ai(
    request: MessageUser,
    _: str = Depends(validate_api_key),
):
    pprint("================================")
    pprint("Received message user")
    pprint(request.model_dump())
    pprint("================================")
    messages_ai = await agent(request.phone_number, request.message)
    
    return MessageAi(message=messages_ai)

# ================================================
# Handle whatsapp get chats
# ================================================

@router.get("/bot-whatsapp/chats/", response_model=Chats)
async def get_chats():
    
    documents = await collection_conversation_state.find().to_list()
    try:
        documents.sort(
        key=lambda x: datetime.fromisoformat(x.get('date', '2024-06-27T18:16:15.847547Z')), 
        reverse=True
        )
    except Exception as e:
        print("Error: ", e)
        pass

    return Chats(chats=documents)

# ================================================
# Handle whatsapp get chat
# ================================================

@router.get("/bot-whatsapp/chat/{phone_number}", response_model=Chat)
async def get_chat(phone_number: str):
    
    document = await collection_conversation_state.find_one({"phone_number": phone_number})
    
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

    return Chat(**document)








