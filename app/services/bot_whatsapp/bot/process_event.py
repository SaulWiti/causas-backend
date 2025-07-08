from ....schemas.bot_whatsapp.event import WhatsappEvent
from ....schemas.bot_whatsapp.event.message import WhatsappMessageType

from pprint import pprint

from .bot_state import (
    is_bot_locked, lock_bot, add_message_chat
)

from ..api import send_message
from ..ai.agent import agent
from ....schemas.bot_whatsapp import WhatsappSendMessageRequest
from ....core.socket import manager
from ....schemas.socket import (
    MessageSocket, MessageType
)
from datetime import (
    datetime, UTC
)
from ....models.bot import Message

async def broadcast_message(
    phone_number: str, content: str, role: str
)->bool:

    try:
        ws_message = MessageSocket(
            phone_number=phone_number,
            type=MessageType.NEW_MESSAGE,
            data=Message(
                role=role,
                content=content,
                date=datetime.now(UTC)
            )
        )
        await manager.broadcast(ws_message)
        print(f"Notificado mensaje de {role} para {phone_number}")
        return True
    except Exception as e:
        print(f"Error notificando mensaje de {role} para {phone_number}: {e}")
        return False

async def get_message_text(event: WhatsappEvent) -> str | None:
    phone_number = event.phone_number
    if not phone_number:
        return None

    if event.message_type == WhatsappMessageType.TEXT:
        return event.message_text

    print("Message type not supported", event.message_type)

    return None

async def process_whatsapp_event(event: WhatsappEvent):
    user_id = event.phone_number
    name = event.user_name
    message_text = await get_message_text(event)
    locked = await is_bot_locked(user_id)

    if message_text:
        await add_message_chat(
            user_id, message_text, "user", name, False
        )
        
        pprint("================================================")
        pprint("Update Message User")
        pprint("================================================")
        
        await broadcast_message(user_id, message_text, "user")
        
        pprint("================================================")
        pprint("Broadcast Message User")
        pprint("================================================")
           
    if user_id and message_text and not locked:        
        message_ai = await agent(user_id, message_text)

        await send_message(user_id, message_ai)

        pprint("================================================")
        pprint("Send Message Ai")
        pprint("================================================")

        await add_message_chat(
            user_id, message_ai, "assistant", name, True
        )

        pprint("================================================")
        pprint("Update Message Ai")
        pprint("================================================")
        
        await broadcast_message(user_id, message_ai, "assistant")
        
        pprint("================================================")
        pprint("Broadcast Message Ai")
        pprint("================================================")
        
    else:
        pprint("================================================")
        pprint("No Send Message Ai")
        print("-is_bot_locked: ", str(locked))
        print("-user_id: ", str(user_id))
        print("-name: ", str(name))
        print("-message_text: ", str(message_text))
        pprint("================================================")

async def process_whatsapp_message(message: WhatsappSendMessageRequest):
    
    await lock_bot(message.phone_number)
    pprint("================================================")
    pprint("Lock bot")
    pprint("================================================")
    
    await send_message(message.phone_number, message.message)
    pprint("================================================")
    pprint("Send Message")
    pprint("================================================")

    await add_message_chat(message.phone_number, message.message, role="human")
    
    pprint("================================================")
    pprint("Update Message Human")
    pprint("================================================")
    
    await broadcast_message(message.phone_number, message.message, "human")
    
    pprint("================================================")
    pprint("Broadcast Message Human")
    pprint("================================================")