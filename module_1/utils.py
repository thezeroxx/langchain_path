import tkinter as tk
from tkinter import filedialog
from langchain.messages import HumanMessage, AIMessage
from langchain.tools import tool, ToolRuntime
import base64
import os
from PIL import Image
import io
import tavily
from models import llm_image
from langchain.messages import SystemMessage, ToolMessage
import constants
from typing import Dict, Any
from langgraph.types import Command
from typing import Literal, List, Union
import sys
import json
from langchain_core.messages import message_to_dict


def func1() -> Union[str, bytes]:
    """
Opens a file dialog for the user to select a photo of their fridge contents or groceries. 
Returns the image in base64 format for subsequent visual analysis.
"""

    print('***Please, enter an image')
    root = tk.Tk()
    root.withdraw()
    file_types = [
        ("Pictures", "*.png *.jpg *.jpeg *.webp"),
        ("All files", "*.*")
    ]
    file_path = filedialog.askopenfilename(
        title='Выберите файл',
        filetypes=file_types,
        initialdir=os.getcwd()
    )
    root.destroy()
    if file_path:
        img = Image.open(file_path)
        img.thumbnail((768, 768), Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=80)
        return base64.b64encode(buffer.getvalue())
    return 'User didnt select any photo. Try again'

def func2(image: Union[str, bytes]) -> List[Any]:
    '''Gets an image subscription (table-like) by it's binary format. Takes an image argument as bytes-like string -- u can get it from the get_compressed_image()'''
    if isinstance(image, bytes):
        print('***Getting an image')
        message = HumanMessage(
        content=[
            {"type": "text", "text": "Опиши фото"},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image.decode('utf-8')}"
                    }
                }
            ]
        )

        response = llm_image.invoke([SystemMessage(constants.image_prompt), message])
        print('***Perfect!')
        return response.content
    return "User didn't select any photo."



@tool
def web_search(food_list: str, allergens: List[str]) -> Dict[str, Any]:
    '''Используй для поиска рецептов в открытом доступе'''
    print('***Searching a web')
    tav = tavily.TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    request = f'recipes with {food_list.split(',')} and without {allergens}'
    response =  tav.search(query=request, max_results=5, include_raw_content=False, search_depth='advanced')
    return [f'{num}. {recipe.get('title')}\nСсылка: {recipe.get('url')}'for num, recipe in enumerate(response['results'], 1)]


@tool
def update_state(key: Literal["food_list", "allergies"], value: str, runtime: ToolRuntime) -> Command:
    '''Используй для того чтобы обновить состояние видом key-value, где key -- ключевое слово, value -- значение.'''
    print('***Updating the state')
    value = (value, value.split(', '))[key=="allergies"]
    return Command[tuple[()]](
        update={
            key: value,
            'messages': [ToolMessage(f'key {key} was updated successfully', tool_call_id=runtime.tool_call_id)]
        }
    )


@tool
def read_state(key: Literal['allergies', 'food_list'], runtime: ToolRuntime) -> str:
    '''Используй, чтобы прочитать данные из состояния'''
    return runtime.state.get(key, f'no {key} found in the state')

@tool
def get_food_list() -> List[Any]:
    '''Используй, чтобы запросить у пользователя фото холодильника'''
    return func2(func1())

def check(llm):
    print('***Checking')
    try:
        llm.invoke(input=[HumanMessage('say hi. only one word')])
        print("***All Good")
        return True
    except Exception as e:
        print(f'Excepted as {e}')
        sys.exit()
        return False
    
def debugging(dct):
    for pos, msg in enumerate(dct['messages']):
        dct['messages'][pos] = message_to_dict(msg)
    with open('debugging.jsonl', 'a', encoding='utf-8') as file:
        content = json.dumps(dct, ensure_ascii=False, indent=3)
        file.write(content+'\n\n')
