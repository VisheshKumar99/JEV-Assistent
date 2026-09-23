from agent.jev.decision_api import classify_youtube_comment
from agent.jev.typesafe_jev import 


if __name__ == "__main__":

    comment = """
    Great video! I finally understood how Kafka works.
    Can you make a video explaining Kafka consumer groups?
    """

    result = classify_youtube_comment(comment)

    print("\nYouTube Comment Classification")
    print("-" * 40)

    # print("Comment:", result["comment"])
    # print("Category:", result["category"])
