import asyncio
import json
import time
from pathlib import Path

import websockets

from agent.llm.service import classify_one
from agent.jev.decision_api import classify_youtube_comment


ROOT = Path(__file__).resolve().parent.parent
COMMENTS_FILE = ROOT / "youtube_comments.json"

HOST = "localhost"
PORT = 8765

CATEGORIES = (
    "Praise",
    "Criticism",
    "Question",
    "Suggestion",
    "Spam / Promotion",
    "Toxicity",
    "Humor",
    "Personal Story",
    "Technical Issue",
    "Other",
)

def load_comments() -> list[str]:
    """Read the comment strings from youtube_comments.json."""
    data = json.loads(COMMENTS_FILE.read_text(encoding="utf-8"))
    return [row["comment"] for row in data if row.get("comment")]


COMMENTS = load_comments()

TOTAL = len(COMMENTS)


class ModelStats:

    def __init__(self, model: str):
        self.model = model
        self.counts = {
            category: 0
            for category in CATEGORIES
        }
        self.processed = 0
        self.total_ms = 0.0

    def add(
        self,
        elapsed_ms: float,
        category: str,
    ):
        self.processed += 1
        self.total_ms += elapsed_ms

        if category in self.counts:
            self.counts[category] += 1
        else:
            self.counts["Other"] += 1

    def snapshot(self, total: int):

        seconds = self.total_ms / 1000

        speed = (
            self.processed / seconds
            if seconds > 0
            else 0
        )

        return {
            "type": "stats",
            "model": self.model,
            "processed": self.processed,
            "total": total,
            "time_seconds": round(seconds, 2),
            "speed": round(speed, 2),
            "counts": self.counts,
        }


async def run_jev(websocket, comments):

    stats = ModelStats("jev")

    for comment in comments:

        start = time.perf_counter()

        try:
            result = await asyncio.to_thread(
                classify_youtube_comment,
                comment,
            )
            # print("coment", result["comment"])
            # print("JEV category", result["category"])

            category = result["category"]

        except Exception as e:

            print("JEV error:", e)

            category = "Other"

        elapsed_ms = (
            time.perf_counter() - start
        ) * 1000

        stats.add(
            elapsed_ms,
            category,
        )

        # print(
        #     f"[JEV] "
        #     f"{category} "
        #     f"{elapsed_ms:.2f}ms"
        # )

        await websocket.send(
            json.dumps(
                stats.snapshot(len(comments))
            )
        )


async def run_llm(websocket, comments):

    stats = ModelStats("llm")

    for comment in comments:

        start = time.perf_counter()

        try:

            category = await asyncio.to_thread(
                classify_one,
                comment,
            )

        except Exception as e:

            print("LLM error:", e)

            category = "Other"

        elapsed_ms = (
            time.perf_counter() - start
        ) * 1000

        stats.add(
            elapsed_ms,
            category,
        )

        # print(
        #     f"[LLM] "
        #     f"{category} "
        #     f"{elapsed_ms:.2f}ms"
        # )

        await websocket.send(
            json.dumps(
                stats.snapshot(len(comments))
            )
        )


async def process(websocket):

    await websocket.send(
        json.dumps({
            "type": "start",
            "total": TOTAL,
        })
    )

    # Both models process the EXACT SAME comments.
    await asyncio.gather(
        run_jev(websocket, COMMENTS),
        run_llm(websocket, COMMENTS),
    )

    await websocket.send(
        json.dumps({
            "type": "done",
            "total": TOTAL,
        })
    )


async def handler(websocket):

    try:

        async for message in websocket:

            data = json.loads(message)

            if data.get("action") == "start":
                await process(websocket)

    except websockets.ConnectionClosed:
        pass


async def main():

    print(
        f"WebSocket server running at "
        f"ws://{HOST}:{PORT}"
    )

    async with websockets.serve(
        handler,
        HOST,
        PORT,
    ):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())