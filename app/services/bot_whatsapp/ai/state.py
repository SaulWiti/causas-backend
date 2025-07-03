from typing import Annotated, Optional
from langgraph.store.base import Op
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class State(TypedDict):
    nodo:str
    phone_number: str
    messages: Annotated[list[BaseMessage], add_messages]
    causa: dict
    
class PartialState(TypedDict, total=False):
    nodo:Optional[str]
    phone_number: Optional[str]
    messages: Optional[Annotated[list[BaseMessage], add_messages]]
    causa: Optional[dict]
