from agent.llm.client import ask_llm
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


def normalize_category(text: str) -> str:
    """Return the matching category name, or 'Other' if none matches."""
    cleaned = text.strip().strip("`\"'")
    for category in CATEGORIES:
        if cleaned.casefold() == category.casefold():
            return category
    return "Other"


def classify_one(comment: str, provider: str | None = None) -> str:
    """Classify a single comment and return one category."""
    prompt = COMMENT_PROMPT.format(comment=comment)
    reply = ask_llm(prompt)
    return normalize_category(reply)
