from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import START, StateGraph

from app.db import db
from .checkpointer import AsyncMongoDBSaver

from .state import State
from .nodes import (
    principal, tool_node_principal,
    especialista, tool_node_especialista
)
from .edges import (
    get_state_init, get_state_principal,
    get_state_especialista
)
from ..bot.bot_state import lock_bot

async def agent(
    user_id: str, message: str
)->str:
    try:
        workflow = StateGraph(State)

        # Nodes
        workflow.add_node("principal", principal)
        workflow.add_node("tool_principal", tool_node_principal)
        workflow.add_node("especialista", especialista)
        workflow.add_node("tool_especialista", tool_node_especialista)

        # Edges
        workflow.add_conditional_edges(START, get_state_init)
        workflow.add_conditional_edges("principal", get_state_principal)
        workflow.add_edge("tool_principal", "principal")
        workflow.add_conditional_edges("especialista", get_state_especialista)
        workflow.add_edge("tool_especialista", "especialista")

        # Chepointer
        checkpointer = AsyncMongoDBSaver(db)
        graph = workflow.compile(checkpointer=checkpointer)

        config: RunnableConfig = {
            "configurable": {"thread_id": user_id},
            # "callbacks": [tracer],
        }

        initial_state = {
            "messages": [HumanMessage(content=message)],
            "phone_number": user_id
        }

        final_state = await graph.ainvoke(initial_state, config=config)

        message_ai = final_state["messages"][-1].content

        return message_ai
    except Exception as e:
        print(e)
        await lock_bot(user_id)
        return "Lo siento, algo salió mal. Ya he notificado al equipo. Te responderán a la brevedad (normalmente en menos de 24 horas)."