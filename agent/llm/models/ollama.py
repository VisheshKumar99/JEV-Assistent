from langchain_ollama import ChatOllama

from agent.config import settings


def get_ollama_model():
    return ChatOllama(
        model=settings.OLLAMA_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
        temperature=0,
    )
