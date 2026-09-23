"""Quick manual check of the JEV classifier on a single comment."""

from agent.jev.decision_api import classify_youtube_comment


if __name__ == "__main__":
    comment = "Great video! I finally understood how Kafka works."

    result = classify_youtube_comment(comment)

    print("YouTube Comment Classification")
    print("-" * 40)
    print("Comment: ", result["comment"])
    print("Category:", result["category"])
