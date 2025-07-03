from .state import (
    State, PartialState
)
from .tools import (
    tools_principal, tools_especialista
)
from .llm import gpt_4o
from .prompts import node_prompts

from langchain_core.prompts import (
    ChatPromptTemplate, MessagesPlaceholder
)
from langgraph.prebuilt import ToolNode, tool_node

from langchain_core.messages import (
    AIMessage, HumanMessage, ToolMessage
)

from json import loads

async def principal(
    state:State
)->PartialState:

    messages = state["messages"]

    last_message = messages[-1]

    if isinstance(last_message, ToolMessage):
        
        return {
            "causa":loads(last_message.content),
            "nodo":"especialista"
        }
    
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", node_prompts.chat_principal.system),
            MessagesPlaceholder("messages"),
        ]
    )

    llm = gpt_4o.bind_tools(tools_principal)

    chain = prompt | llm

    response = await chain.ainvoke(
        {
            "messages": messages,
        }
    )

    return {
        "messages": [response]
    }

async def especialista(
    state: State
)->PartialState:
    
    messages = state["messages"]
    
    tipo_causa = state["causa"]["tipo"]
    
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", node_prompts.chat_especialista.system),
            MessagesPlaceholder("messages"),
        ]
    )

    llm = gpt_4o.bind_tools(tools_especialista)

    chain = prompt | llm

    response = await chain.ainvoke(
        {
            "messages": messages,
            "tipo_causa": tipo_causa
        }
    )

    return {
        "messages": [response],
    }

tool_node_principal = ToolNode(tools_principal)
tool_node_especialista = ToolNode(tools_especialista)