


if __name__ == "__main__":

    comment = """
    Great video! I finally understood how Kafka works.
    Can you make a video explaining Kafka consumer groups?
    """

    result = classify_youtube_comment(comment)

    print("\nYouTube Comment Classification")
    print("-" * 40)

    print("Comment:", result["comment"])
    print("Sentiment:", result["sentiment"])
    print("Intent:", result["intent"])
    print("Toxicity:", result["toxicity"])
    print(
        "Needs Reply Probability:",
        result["needs_reply_probability"]
    )