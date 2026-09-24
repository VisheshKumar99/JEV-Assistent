"""JEV classification via the local `laya` Router.

Same contract as decision_api.py (comment -> one category), but instead of the
OpenRouter HTTP endpoint it runs the decision locally through laya's Router.
"""

from dotenv import load_dotenv
from laya import Router

load_dotenv()

# Preload keeps the model resident so the first call doesn't pay a swap delay.
router = Router(preload=True)

# The 10 shared categories. Values are used both as the allowed choices and as
# the per-choice criteria the router scores against.
CATEGORIES = {
    "Praise": "Positive feedback, appreciation, compliments, or expressions of enjoyment.",
    "Criticism": "Negative feedback, complaints, call-outs, or structural critiques.",
    "Question": "Inquiries, requests for clarification, or general questions.",
    "Suggestion": "Recommendations, ideas for improvement, or future content requests.",
    "Spam / Promotion": "Unrelated advertisements, link drops, or repetitive bot messages.",
    "Toxicity": "Insults, hate speech, offensive behavior, or hostile attacks.",
    "Humor": "Jokes, memes, sarcasm, puns, or funny observations.",
    "Personal Story": "Sharing individual life experiences, anecdotes, or relatable personal updates.",
    "Technical Issue": "Reporting audio/video sync errors, playback bugs, or broken links.",
    "Other": "Comments that do not match any definition above.",
}


def classify_youtube_comment(comment: str):
    """Classify one comment into exactly one category using laya."""
    state = {"comment": comment}

    questions = {
        "category": {
            "type": "choice",
            "instructions": "Classify this YouTube comment into exactly one category.",
            "criteria": CATEGORIES,
        }
    }

    res = router.predict(state, questions)

    choice = res["answers"]["category"]["choice"]

    return {
        "comment": comment,
        "category": choice if choice in CATEGORIES else "Other",
    }
