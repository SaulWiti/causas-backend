from fastapi import (
    APIRouter, 
    Request,
    Query,
    BackgroundTasks,
)
from pprint import pprint

from ..schemas.bot_whatsapp import (
    ACKResponse, MessageAi, MessageUser
)
from ..schemas.bot_whatsapp.event import WhatsappEvent
from ..schemas.bot_whatsapp.event.message import WhatsappMessageType

from ..services.bot_whatsapp.agent import agent
from ..core.config import config
from ..core import http

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

# ================================================
# Handle whatsapp webhook events
# ================================================


async def get_message_text(event: WhatsappEvent) -> str | None:
    phone_number = event.phone_number
    if not phone_number:
        return None

    if event.message_type == WhatsappMessageType.TEXT:
        return event.message_text

    print("Message type not supported", event.message_type)

    return None

async def send_message(phone_number: str, message: str):
    url = f"{config.graph_facebook_url}/{config.whatsapp_phone_id}/messages"
    print("================================================")
    print("Sending message")
    print(f"To {phone_number}")
    print(f"Message: {message}")
    print(f"POST {url}")
    print("================================================")
    headers = {
        "Authorization": f"Bearer {config.whatsapp_api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone_number,
        "type": "text",
        "text": {"body": message},
    }
    response = await http.post(url, headers=headers, data=data)
    pprint(response)
    print("================================================")
    return response

async def process_whatsapp_event(event: WhatsappEvent):
    user_id = event.phone_number
    message_text = await get_message_text(event)

    if user_id and message_text:        
        message_ai = await agent(user_id, message_text)

        await send_message(user_id, message_ai)
        
        pprint("================================================")
        pprint("Send Message Ai")
        pprint("================================================")

    else:
        pprint("================================================")
        pprint("Error Send Message Ai")
        pprint("================================================")

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


@router.post("/bot-whatsapp/message/", response_model=MessageAi)
async def get_message_ai(
    request: MessageUser
):
    pprint("================================")
    pprint("Received message user")
    pprint(request.model_dump())
    pprint("================================")
    messages_ai = await agent(request.user_id, request.message)
    
    return MessageAi(message=messages_ai)







