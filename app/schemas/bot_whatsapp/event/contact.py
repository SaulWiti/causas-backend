from enum import Enum

from pydantic import BaseModel


class FieldType(Enum):
    HOME = "HOME"
    WORK = "WORK"


class WhatsappMessageContactAddress(BaseModel):
    city: str | None = None
    country: str | None = None
    country_code: str | None = None
    state: str | None = None
    street: str | None = None
    type: FieldType | None = None
    zip: str | None = None


class WhatsappMessageContactEmail(BaseModel):
    email: str
    type: FieldType


class WhatsappMessageContactName(BaseModel):
    formatted_name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    middle_name: str | None = None
    suffix: str | None = None
    prefix: str | None = None


class WhatsappMessageContactOrg(BaseModel):
    company: str | None = None
    department: str | None = None
    title: str | None = None


class WhatsappMessageContactPhone(BaseModel):
    phone: str
    wa_id: str
    type: FieldType


class WhatsappMessageContactUrl(BaseModel):
    url: str
    type: FieldType


class WhatsappMessageContact(BaseModel):
    addresses: list[WhatsappMessageContactAddress] | None = None
    birthday: str | None = None
    emails: list[WhatsappMessageContactEmail] | None = None
    name: WhatsappMessageContactName | None = None
    org: WhatsappMessageContactOrg | None = None
    phones: list[WhatsappMessageContactPhone] | None = None
    urls: list[WhatsappMessageContactUrl] | None = None
