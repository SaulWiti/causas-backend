from typing import Literal

from pydantic import BaseModel, computed_field

from .message import WhatsappMessage, WhatsappMessageType


class WhatsappEventMetadata(BaseModel):
    display_phone_number: str
    phone_number_id: str


class WhatsappProfile(BaseModel):
    name: str


class WhatsappContact(BaseModel):
    profile: WhatsappProfile
    wa_id: str


class WhatsappStatus(BaseModel):
    id: str
    status: Literal["read", "delivered", "sent", "failed"]
    recipient_id: str
    timestamp: str


class WhatsappEventChangeValue(BaseModel):
    messaging_product: str
    metadata: WhatsappEventMetadata
    contacts: list[WhatsappContact] | None = None
    messages: list[WhatsappMessage] | None = None
    statuses: list[WhatsappStatus] | None = None


class WhatsappEventChange(BaseModel):
    value: WhatsappEventChangeValue


class WhatsappEventEntry(BaseModel):
    id: str
    changes: list[WhatsappEventChange]


class WhatsappEvent(BaseModel):
    object: str
    entry: list[WhatsappEventEntry]

    @computed_field
    @property
    def phone_number(self) -> str | None:
        try:
            contacts = self.entry[0].changes[0].value.contacts
            if contacts:
                return contacts[0].wa_id
            return None
        except Exception:
            return None

    @computed_field
    @property
    def message_type(self) -> WhatsappMessageType | None:
        try:
            messages = self.entry[0].changes[0].value.messages
            if messages:
                return messages[0].type_
            return None
        except Exception:
            return None

    @computed_field
    @property
    def message_text(self) -> str | None:
        try:
            messages = self.entry[0].changes[0].value.messages
            if messages and messages[0].text:
                return messages[0].text.body
            return None
        except Exception:
            return None

    @computed_field
    @property
    def status(self) -> WhatsappStatus | None:
        try:
            statuses = self.entry[0].changes[0].value.statuses
            if statuses:
                return statuses[0]
            return None
        except Exception:
            return None

    @computed_field
    @property
    def file_id(self) -> str | None:
        try:
            messages = self.entry[0].changes[0].value.messages
            if messages and messages[0].document:
                return messages[0].document.id
            return None
        except Exception:
            return None