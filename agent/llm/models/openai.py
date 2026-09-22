from langchain_openai import ChatOpenAI

from agent.config import settings


def get_openai_model():
    if not settings.OPENAI_API_KEY:
        raise RuntimeError(
            "OPENAI_API_KEY is not configured. Add it to .env before using OpenAI."
        )

    return ChatOpenAI(
        model=settings.OPENAI_MODEL,
        api_key=settings.OPENAI_API_KEY,
        temperature=0,
    )
