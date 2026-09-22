import os
from dotenv import load_dotenv
from typesafe_sdk import Choice, TypeSafeClient

from agent.llm.service import CATEGORIES

load_dotenv()

if not os.getenv("TYPESAFE_API_KEY"):
    raise ValueError("TYPESAFE_API_KEY is not set.")

client = TypeSafeClient()


# Same 10 categories used by the LLM prompt, so both models can be compared.
CATEGORY_CRITERIA = {
    "Praise": "Appreciation or compliments for the creator or content.",
    "Criticism": "Negative opinion or complaint about the content.",
    "Question": "Asking for information or clarification.",
    "Suggestion": "Proposing an idea or improvement.",
    "Spam / Promotion": "Promotional, repetitive, or advertising content.",
    "Toxicity": "Insulting, hateful, threatening, or abusive language.",
    "Humor": "A joke or something intended to be funny.",
    "Personal Story": "Sharing a personal experience or anecdote.",
    "Technical Issue": "Reporting a bug, error, or technical problem.",
    "Other": "Does not fit any of the categories above.",
}


def classify_youtube_comment(comment: str):
    response = client.system_one(
        state={
            "comment": comment
        },
        questions={
            "category": Choice(
                instructions="Classify this YouTube comment into exactly one category.",
                criteria=CATEGORY_CRITERIA
            )
        }
    )

    category = response.answers["category"].choice

    return {
        "comment": comment,
        "category": category if category in CATEGORIES else "Other"
    }
