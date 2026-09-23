import os
import json

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")

url = "https://openrouter.ai/api/alpha/decisions"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

payload = {
    "model": "typesafe/jev-1.13",
    "state": "This video is amazing! I learned so much from it.",
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

print("payload", payload)

response = requests.post(url, headers=headers, data=json.dumps(payload))
data = response.json()

choice = data["answers"]["category"]["choice"]
print("choice:", choice)
