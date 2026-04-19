from langgraph.graph import StateGraph,START,END
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver # make the persistance you have three option 
                                                    #1. InMemorySaver:
                                                    #2.SqliteSaver : for proto type 
                                                    #3.PostgresSaver : for production purpose.
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage,HumanMessage
from langgraph.graph.message import add_messages
from typing import TypedDict,Annotated,Literal
from pydantic import BaseModel
import sqlite3



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

#creating a database
connection=sqlite3.connect(database='chatbot.db',check_same_thread=False) # Since sqlite works on same thread so it required to turn off
#checkpoint
#checkpointer=InMemorySaver()
checkpointer=SqliteSaver(conn=connection)
graph=StateGraph(ChatState)

#adding a nodes

graph.add_node("Chat_node",chat_node)

#adding an edges
graph.add_edge(START,"Chat_node")
graph.add_edge("Chat_node",END)
chatmodel=graph.compile(checkpointer=checkpointer)



def retrive_all_threads():
    all_threads=set()
    for check in checkpointer.list(None):# i need checpoints for all the treads
        all_threads.add(check.config['configurable']['thread_id'])
    return list(all_threads)


