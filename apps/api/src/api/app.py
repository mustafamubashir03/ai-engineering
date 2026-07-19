from api.api.endpoints import api_router
from fastapi import FastAPI


import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(ascitime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# def run_llm(provider, model_name, messages, max_tokens=1000):
#     if provider == "openai":
#         client = OpenAI(api_key=config.OPENAI_API_KEY)
#         return client.chat.completions.create(model=model_name,messages=messages, max_completion_tokens=max_tokens).choices[0].message.content
#     elif provider == "google":
#         client = genai.Client(api_key=config.GOOGLE_API_KEY)
#         return client.models.generate_content(model=model_name,contents=[messages["content"] for message in messages]).text
#     elif provider == "groq":
#         client = Groq(api_key=config.OPENAI_API_KEY)


# class ChatRequest(BaseModel):
#     provider:str
#     model_name:str
#     messages:List[dict]

# class ChatResponse(BaseModel):
#     message:str

from api.api.middleware import RequestIDMiddleware

app = FastAPI()
app.add_middleware(RequestIDMiddleware)
app.include_router(api_router)


