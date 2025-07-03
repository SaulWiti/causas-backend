from typing import Literal

from langgraph.graph import END

from .state import State

def get_state_init(
    state: State,
) -> Literal["principal",  "especialista", "__end__"]:
    nodo = state.get("nodo", "principal")

    if nodo in {"principal", "especialista"}:
        return nodo

    return END

def get_state_principal(
        state: State
) -> Literal["tool_principal", "especialista", "__end__"]:
    
    nodo = state.get("nodo", "principal")

    if nodo == "especialista":
        return nodo

    last_message = state["messages"][-1]

    if last_message.tool_calls:
        return "tool_principal"

    return END

def get_state_especialista(
        state: State
) -> Literal["tool_especialista", "principal", "__end__"]:

    nodo = state["nodo"]
    if nodo == "principal":
        return nodo
    
    last_message = state["messages"][-1]

    if last_message.tool_calls:
        return "tool_especialista"

    return END