"""LAYA classifier that returns one of the 10 shared categories.

Thin wrapper over laya_decision_api.classify_youtube_comment so the backend can
get a single category string, matching the LLM classifier's contract.
"""

from agent.jev.laya_decision_api import classify_youtube_comment


def classify_one(comment: str) -> str:
    """Classify a single comment into exactly one shared category."""
    return classify_youtube_comment(comment)["category"]
