from datetime import datetime
from pydantic import BaseModel
from typing import Literal

class Message(BaseModel):
    role: Literal["user", "assistant", "human"]
    content: str
    date: datetime
    self_view: None|bool = None

class ConversationState(BaseModel):
    phone_number: str
    name:None|str = None
    date: None|datetime = None
    messages: None|list[Message] = None
    locked: bool = False
    self_count_not_viewed: int = 0

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
                        "date": "2025-06-16T10:00:00",
                        "self_view": False
                    }
                ],
                "locked": False,
                "self_count_not_viewed": 0
            }
        }