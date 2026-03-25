from fastapi import FastAPI
from chatbot import chat_with_ai

app = FastAPI()

@app.get("/chat")
def chat(q: str):
    return {"response": chat_with_ai(q)}
