from langgraph.graph import StateGraph,START,END
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing import TypedDict,Annotated,Literal
from pydantic import BaseModel


load_dotenv()

class ChatState(TypedDict):
    messages:Annotated[list[BaseMessage],add_messages]


model=ChatOpenAI()

def chat_node(state:ChatState):
    #messages
    message=state['messages']

    #response
    response=model.invoke(message)
    #storing the response
    return {'messages':[response]}

#checkpoint
checkpointer=InMemorySaver()
graph=StateGraph(ChatState)

#adding a nodes

graph.add_node("Chat_node",chat_node)

#adding an edges
graph.add_edge(START,"Chat_node")
graph.add_edge("Chat_node",END)

chatmodel=graph.compile(checkpointer=checkpointer)