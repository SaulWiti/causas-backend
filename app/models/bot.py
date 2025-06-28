from datetime import datetime
from pydantic import BaseModel
from typing import Literal

class Message(BaseModel):
    role: Literal["user", "assistant", "human"]
    content: str
    date: datetime

class ConversationState(BaseModel):
    phone_number: str
    date: None|datetime = None
    messages: None|list[Message] = None
    locked: bool = False

    class Config:
        arbitrary_types_allowed = True  
        json_schema_extra = {
            "example": {
                "phone_number": "56912345678",
                "date": "2025-06-16T10:00:00",
                "messages": [
                    {
                        "role": "user",
                        "content": "Hola",
                        "date": "2025-06-16T10:00:00"
                    }
                ],
                "locked": False
            }
        }