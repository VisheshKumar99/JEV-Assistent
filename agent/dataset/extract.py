from datasets import load_dataset
import json

dataset = load_dataset(
    "vnkat/youtube-comment-sentiment",
    split="train"
)

dev_dataset = dataset.shuffle(seed=42).select(range(10_000))

comments = [
    {
        "comment": row["CommentText"],
        "id": str(i)
    }
    for i, row in enumerate(dev_dataset)
]

print("comments", len(comments))

with open("youtube_comments.json", "w", encoding="utf-8") as f:
    json.dump(comments, f, ensure_ascii=False)

print(f"Saved {len(comments)} comments")