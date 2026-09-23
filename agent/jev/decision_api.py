import os
import requests
import json

from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

OPENROUTER_URL = "https://openrouter.ai/api/alpha/decisions"

headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
}

CATEGORIES = {
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

    payload = {
        "model": "typesafe/jev-1.13",
        "state": comment,
        "questions": {
            "category": {
                "type": "choice",
                "instructions": "Classify this YouTube comment into exactly one category.",
                "criteria": {
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
                },
            }
        },
    }

    response = requests.post(OPENROUTER_URL, headers=headers, data=json.dumps(payload))
    response.raise_for_status()
    data = response.json()

    choice = data["answers"]["category"]["choice"]

    return {
        "comment": comment,
        "category": choice if choice in CATEGORIES else "Other",
    }