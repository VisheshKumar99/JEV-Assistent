from agent.llm.models.ollama import get_ollama_model
from agent.llm.models.openai import get_openai_model
from agent.llm.prompts import COMMENT_PROMPT


def classify(model, comment):

    prompt = COMMENT_PROMPT.format(
        comment=comment
    )

    response = model.invoke(prompt)

    return response.content


if __name__ == "__main__":

    comment = """
    Too good Bro
    """

    print("\n===== OLLAMA =====")

    ollama = get_ollama_model()

    print(
        classify(
            ollama,
            comment
        )
    )

    print("\n===== OPENAI =====")

    # openai = get_openai_model()

    # print(
    #     classify(
    #         openai,
    #         comment
    #     )
    # )