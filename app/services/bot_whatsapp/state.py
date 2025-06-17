from typing import Annotated, Optional

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class State(TypedDict):
    nodo:str
    messages: Annotated[list[BaseMessage], add_messages]
    


class PartialState(TypedDict, total=False):
    nodo:str
    messages: Optional[Annotated[list[BaseMessage], add_messages]]