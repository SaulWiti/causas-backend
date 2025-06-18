from enum import Enum

from pydantic import BaseModel, Field

from .contact import WhatsappMessageContact


class WhatsappMessageType(Enum):
    TEXT = "text"
    REACTION = "reaction"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    STICKER = "sticker"
    LOCATION = "location"
    UNKNOWN = "unknown"
    BUTTON = "button"
    INTERACTIVE = "interactive"


class WhatsappMessageInteractiveType(Enum):
    LIST_REPLY = "list_reply"
    BUTTON_REPLY = "button_reply"


class WhatsappMessageText(BaseModel):
    body: str


class WhatsappMessageReaction(BaseModel):
    message_id: str
    emoji: str


class WhatsappMessageMedia(BaseModel):
    mime_type: str
    sha256: str
    id: str
    filename: str | None = None


class WhatsappMessageImage(WhatsappMessageMedia):
    caption: str


class WhatsappMessageLocation(BaseModel):
    latitude: float
    longitude: float
    name: str
    address: str


class WhatsappMessageButton(BaseModel):
    text: str
    payload: str


class WhatsappMessageInteractiveListReply(BaseModel):
    id: str
    title: str
    description: str
    image_url: str


class WhatsappMessageInteractiveButtonReply(BaseModel):
    id: str
    title: str


class WhatsappMessageInteractive(BaseModel):
    type: WhatsappMessageInteractiveType
    list_reply: WhatsappMessageInteractiveListReply | None = None
    button_reply: WhatsappMessageInteractiveButtonReply | None = None


class WhatsappMessageReferral(BaseModel):
    source_url: str
    source_id: str
    source_type: str
    headline: str
    body: str
    media_type: str
    image_url: str
    video_url: str
    thumbnail_url: str
    ctwa_clid: str


class WhatsappMessage(BaseModel):
    from_: str = Field(alias="from")
    id: str
    timestamp: str
    type_: WhatsappMessageType | None = Field(alias="type", default=None)
    text: WhatsappMessageText | None = None
    reaction: WhatsappMessageReaction | None = None
    image: WhatsappMessageImage | None = None
    sticker: WhatsappMessageMedia | None = None
    document: WhatsappMessageMedia | None = None
    location: WhatsappMessageLocation | None = None
    contacts: list[WhatsappMessageContact] | None = None
    button: WhatsappMessageButton | None = None
    interactive: WhatsappMessageInteractive | None = None
    referral: WhatsappMessageReferral | None = None