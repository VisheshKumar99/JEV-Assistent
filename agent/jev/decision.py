import os
from dotenv import load_dotenv
from typesafe_sdk import Choice, Score, Noul, TypeSafeClient

load_dotenv()

if not os.getenv("TYPESAFE_API_KEY"):
    raise ValueError("TYPESAFE_API_KEY is not set.")

client = TypeSafeClient()


def classify_youtube_comment(comment: str):
    response = client.system_one(
        state={
            "comment": comment
        },
        questions={
            "sentiment": Choice(
                instructions="What is the overall sentiment of this YouTube comment?",
                criteria={
                    "positive": "The commenter expresses appreciation, satisfaction, excitement, or praise.",
                    "neutral": "The commenter is primarily stating information or asking something without clear positive or negative sentiment.",
                    "negative": "The commenter expresses dissatisfaction, criticism, anger, or dislike."
                }
            ),

            "intent": Choice(
                instructions="What is the primary intent of this YouTube comment?",
                criteria={
                    "question": "The commenter is asking for information or clarification.",
                    "feedback": "The commenter is giving an opinion, suggestion, or criticism about the content.",
                    "praise": "The commenter is mainly appreciating or complimenting the creator or content.",
                    "spam": "The comment appears promotional, repetitive, irrelevant, or intended to advertise something."
                }
            ),

            "toxicity": Score(
                instructions="How toxic or abusive is this comment?",
                criteria=[
                    "Low toxicity: normal conversation, criticism, or harmless disagreement.",
                    "Medium toxicity: insulting, hostile, or aggressive language.",
                    "High toxicity: severe harassment, threats, hateful or extremely abusive language."
                ]
            ),

            "needs_reply": Noul(
                instructions="Does this comment require a response from the creator?"
            )
        }
    )

    return {
        "comment": comment,
        "sentiment": response.answers["sentiment"].choice,
        "intent": response.answers["intent"].choice,
        "toxicity": response.answers["toxicity"].score,
        "needs_reply_probability": response.answers["needs_reply"].noul
    }


