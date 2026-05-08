print('***Script is being ran...')


import os
from langchain.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.messages import BaseMessage, message_to_dict
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain.agents import create_agent
from pydantic import BaseModel
from langchain.tools import tool
import tavily
from typing import Any, Dict, Annotated, List
from langgraph.checkpoint.memory import InMemorySaver
import utils
import constants
from models import *
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
import uuid
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
import sys
import json
from langgraph.types import Command
from datetime import datetime
import operator


load_dotenv()


os.environ["MSGPACK_ALLOWED_MODULES"] = "__main__"


with open('debugging.jsonl', 'a') as file:
    json.dump({'session': datetime.now().isoformat()}, file)

def reductor(current: List[BaseMessage], new: List[BaseMessage]) -> List[BaseMessage]:
    all_messages = add_messages(current, new)
    return all_messages[-6:]

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], reductor]
    food_list: str
    allergies: Annotated[list, operator.add]



agent = create_agent(
    model=llm_text,
    tools=[utils.get_food_list, utils.web_search, utils.update_state, utils.read_state],
    checkpointer=InMemorySaver(), 
    system_prompt=constants.text_prompt, 
    state_schema=AgentState
)

conf = {'configurable': {'thread_id': str(uuid.uuid4())}}

utils.check(llm_image)
while True:
    current_state = agent.get_state(conf).values
    response = agent.invoke(
        {'messages': [HumanMessage(input('User: '))]},
        config=conf)
    print("AI: ", response['messages'][-1].content)
    utils.debugging(response.copy())