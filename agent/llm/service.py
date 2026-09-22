from agent.config import settings
from agent.llm.prompts import COMMENT_PROMPT


CATEGORIES = (
    "Praise",
    "Criticism",
    "Question",
    "Suggestion",
    "Spam / Promotion",
    "Toxicity",
    "Humor",
    "Personal Story",
    "Technical Issue",
    "Other",
)


def get_model(provider: str | None = None):
    selected = (provider or settings.LLM_PROVIDER).strip().lower()

    if selected == "ollama":
        from agent.llm.models.ollama import get_ollama_model
        return get_ollama_model()

    if selected == "openai":
        from agent.llm.models.openai import get_openai_model
        return get_openai_model()

    raise ValueError("LLM_PROVIDER must be 'ollama' or 'openai'")


def normalize_category(text: str) -> str:
    """Return the matching category name, or 'Other' if none matches."""
    cleaned = text.strip().strip("`\"'")
    for category in CATEGORIES:
        if cleaned.casefold() == category.casefold():
            return category
    return "Other"


def classify_one(comment: str, provider: str | None = None) -> str:
    """Classify a single comment and return one category."""
    model = get_model(provider)
    prompt = COMMENT_PROMPT.format(comment=comment)
    response = model.invoke(prompt)
    return normalize_category(response.content)
