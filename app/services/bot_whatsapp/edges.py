from typing import Literal

from langgraph.graph import END

from .state import State

def get_state_init(
    state: State,
) -> Literal["principal",  "__end__"]:
    nodo = state.get("nodo", "principal")

    if nodo in {"principal"}:
        return nodo

    return END

def get_state_principal(
        state: State
) -> Literal["tool_principal", "__end__"]:
    
    last_message = state["messages"][-1]

    if last_message.tool_calls:
        return "tool_principal"

    return END