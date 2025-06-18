from pydantic import BaseModel

class ACKResponse(BaseModel):
    message: str

class MessageUser(BaseModel):
    user_id: str
    message: str

class MessageAi(BaseModel):
    message: str