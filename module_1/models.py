from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

llm_image = ChatGoogleGenerativeAI(
    model=os.getenv('GOOGLE_MODEL'),
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0,
    max_tokens=400
)

llm_text = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL"),
    api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0.5,
    base_url='https://openrouter.ai/api/v1',
    default_headers={
        'X-Title': 'MyApp', 
        "HTTP-Referer": 'https://google.com'
    }
)