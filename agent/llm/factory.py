from agent.config import settings
from agent.llm.models.openai import get_openai_model
from agent.llm.models.ollama import get_ollama_model


def get_llm():
    provider = settings.LLM_PROVIDER.lower()

    if provider == "openai":
        return get_openai_model()

    if provider == "ollama":
        return get_ollama_model()

    raise ValueError(
        f"Unsupported LLM provider: {settings.LLM_PROVIDER}"
    )