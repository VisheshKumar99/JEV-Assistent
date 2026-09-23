from agent.llm.factory import get_llm


def ask_llm(prompt: str) -> str:
    llm = get_llm()

    response = llm.invoke(prompt)

    return response.content