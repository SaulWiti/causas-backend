from .state import (
    State, PartialState
)
from .tools import tools_principal
from .llm import gpt_4o
from .prompts import node_prompts

from langchain_core.messages import (
    AIMessage, HumanMessage, ToolMessage
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.prebuilt import ToolNode


async def principal(
    state:State
)->PartialState:

    messages = state["messages"]
    
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
        "messages": [response],
    }

tool_node_principal = ToolNode(tools_principal)