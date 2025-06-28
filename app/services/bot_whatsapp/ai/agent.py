from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import START, StateGraph

from app.db import db
from .checkpointer import AsyncMongoDBSaver

from .state import State
from .nodes import (
    principal, tool_node_principal
)
from .edges import (
    get_state_init, get_state_principal
)

async def agent(
    user_id: str, message: str
)->str:
    workflow = StateGraph(State)

    # Nodes
    workflow.add_node("principal", principal)
    workflow.add_node("tool_principal", tool_node_principal)

    # Edges
    workflow.add_conditional_edges(START, get_state_init)
    workflow.add_conditional_edges("principal", get_state_principal)
    workflow.add_edge("tool_principal", "principal")

    # Chepointer
    checkpointer = AsyncMongoDBSaver(db)
    graph = workflow.compile(checkpointer=checkpointer)

    config: RunnableConfig = {
        "configurable": {"thread_id": user_id},
        # "callbacks": [tracer],
    }

    initial_state = {"messages": [HumanMessage(content=message)]}
    
    final_state = await graph.ainvoke(initial_state, config=config)
    
    message_ai = final_state["messages"][-1].content
    
    return message_ai