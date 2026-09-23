from agent.llm.service import classify_one


if __name__ == "__main__":

    comment = "Too good Bro"

    print("\n===== LLM (OpenRouter) =====")
    print(classify_one(comment))
