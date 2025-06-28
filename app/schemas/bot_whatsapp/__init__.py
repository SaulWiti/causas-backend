from pydantic import BaseModel
from ...models.bot import ConversationState

class ACKResponse(BaseModel):
    message: str

class MessageUser(BaseModel):
    phone_number: str
    message: str

class MessageAi(BaseModel):
    message: str

class WhatsappSendMessageRequest(BaseModel):
    phone_number: str
    message: str

class BotLockRequest(BaseModel):
    phone_number: str

class Chats(BaseModel):
    chats: list[ConversationState]

class Chat(ConversationState):
    pass