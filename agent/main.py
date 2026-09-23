"""Quick manual check of the LLM classifier on a single comment."""

from agent.llm.service import classify_one


if __name__ == "__main__":
    comment = "Too good Bro"

    print("===== LLM (via configured provider) =====")
    print(classify_one(comment))
