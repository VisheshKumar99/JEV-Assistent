import os

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("OPENAI_API_KEY is not set.")

LLM_URL = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1") + "/chat/completions"
LLM_MODEL = os.getenv("OPENAI_MODEL", "openai/gpt-6-sol")


def ask_llm(prompt: str) -> str:
    """Send a prompt to OpenRouter and return the assistant's text reply."""
    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
    }

    response = requests.post(
        LLM_URL,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        json=payload,
    )
    response.raise_for_status()
    data = response.json()

    return data["choices"][0]["message"]["content"]
