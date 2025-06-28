from datetime import datetime, UTC
from enum import Enum
from typing import List, Optional, Union
from pydantic import BaseModel, Field
from ..models.bot import Message

class MessageType(str, Enum):
    NEW_MESSAGE = "new_message"
    STATUS_UPDATE = "status_update"
    ERROR = "error"
    SYSTEM = "system"

class MessageSocket(BaseModel):
    """Esquema para mensajes WebSocket"""
    type: MessageType = Field(..., description="Tipo de mensaje")
    phone_number: Optional[str] = Field(
        None,
        description="Número de teléfono del chat que se debe actualizar"
    )
    data: Message = Field(
        ..., 
        description="Contenido del mensaje"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Marca de tiempo del mensaje"
    )
    sender: Optional[str] = Field(
        None, 
        description="ID del remitente (opcional)"
    )
    target: Optional[Union[str, List[str]]] = Field(
        None,
        description="ID(s) del/los destinatario(s) (opcional, para mensajes directos)"
    )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "type": "new_message",
                "phone_number": "1234567890",
                "data": {
                    "role": "user",
                    "content": "Hola, ¿cómo estás?",
                    "date": "2025-06-27T11:30:00Z"
                },
                "timestamp": "2025-06-27T11:30:00Z",
                "sender": "user123"
            }
        }