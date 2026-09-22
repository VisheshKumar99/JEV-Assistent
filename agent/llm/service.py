from concurrent.futures import ThreadPoolExecutor
from typing import Any, Iterable

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


class LLMProviderError(RuntimeError):
    """Raised when an LLM provider cannot classify a batch."""


class InvalidCategoryError(LLMProviderError):
    """Raised when a provider returns something outside the category contract."""


def _response_text(response: Any) -> str:
    content = getattr(response, "content", response)
    if isinstance(content, str):
        return content.strip()
    return str(content).strip()


def normalize_category(value: str) -> str:
    """Convert a model response into one of the exact allowed category names."""
    cleaned = value.strip().strip("`\"'")

    for category in CATEGORIES:
        if cleaned.casefold() == category.casefold():
            return category

    # Accept a category returned on its own line, while rejecting explanations.
    for line in value.splitlines():
        line = line.strip().strip("`\"'")
        for category in CATEGORIES:
            if line.casefold() == category.casefold():
                return category

    raise InvalidCategoryError(
        f"Model returned an invalid category: {value!r}. "
        f"Expected one of: {', '.join(CATEGORIES)}"
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


def classify_batch(
    comments: Iterable[str],
    provider: str | None = None,
) -> list[dict[str, str]]:
    """Classify a bounded batch with one provider using bounded concurrency."""
    comment_list = list(comments)
    if not comment_list:
        return []

    selected = (provider or settings.LLM_PROVIDER).strip().lower()
    model = get_model(selected)
    prompts = [COMMENT_PROMPT.format(comment=comment) for comment in comment_list]

    try:
        responses = model.batch(
            prompts,
            config={"max_concurrency": settings.LLM_MAX_CONCURRENCY},
        )
    except Exception as exc:  # provider SDK errors vary by backend
        raise LLMProviderError(
            f"{selected} failed to classify the batch: {exc}"
        ) from exc

    results: list[dict[str, str]] = []
    for comment, response in zip(comment_list, responses, strict=True):
        raw = _response_text(response)
        results.append({
            "comment": comment,
            "category": normalize_category(raw),
        })

    return results


def classify_with_providers(
    comments: Iterable[str],
    providers: Iterable[str],
) -> dict[str, list[dict[str, str]] | str]:
    """Run selected providers concurrently for the same comment batch."""
    comment_list = list(comments)
    provider_list = [provider.strip().lower() for provider in providers]
    output: dict[str, list[dict[str, str]] | str] = {}

    def run(provider: str):
        try:
            return provider, classify_batch(comment_list, provider)
        except Exception as exc:  # keep one provider failure from hiding the other
            return provider, f"{type(exc).__name__}: {exc}"

    with ThreadPoolExecutor(max_workers=len(provider_list)) as executor:
        for provider, result in executor.map(run, provider_list):
            output[provider] = result

    return output
