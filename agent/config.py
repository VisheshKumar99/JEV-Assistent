import os

from dotenv import load_dotenv

load_dotenv()


def _positive_int(name: str, default: int) -> int:
    try:
        value = int(os.getenv(name, str(default)))
    except ValueError:
        return default
    return max(1, value)


class Settings:

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    OPENAI_MODEL = os.getenv(
        "OPENAI_MODEL",
        "gpt-4o-mini"
    )

    OLLAMA_MODEL = os.getenv(
        "OLLAMA_MODEL",
        "qwen2.5:3b"
    )

    OLLAMA_BASE_URL = os.getenv(
        "OLLAMA_BASE_URL",
        "http://localhost:11434"
    )

    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "both").strip().lower()

    LLM_MAX_CONCURRENCY = _positive_int(
        "LLM_MAX_CONCURRENCY",
        4
    )

    HF_DATASET_NAME = os.getenv(
        "HF_DATASET_NAME",
        "AmaanP314/youtube-comment-sentiment"
    )

    HF_DATASET_SPLIT = os.getenv(
        "HF_DATASET_SPLIT",
        "train"
    )

    HF_TEXT_COLUMN = os.getenv(
        "HF_TEXT_COLUMN",
        "CommentText"
    )

    HF_TARGET_COUNT = _positive_int(
        "HF_TARGET_COUNT",
        1_000_000
    )

    HF_MIN_COMMENT_LENGTH = _positive_int(
        "HF_MIN_COMMENT_LENGTH",
        3
    )

    HF_MIN_ASCII_RATIO = float(
        os.getenv("HF_MIN_ASCII_RATIO", "0.9")
    )

    HF_OUTPUT_PATH = os.getenv(
        "HF_OUTPUT_PATH",
        "data/youtube_comments_en.jsonl"
    )


settings = Settings()
