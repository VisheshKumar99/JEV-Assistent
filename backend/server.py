"""Simple WebSocket server that streams JEV vs LLM classification stats.

For every comment it runs the JEV model and the LLM model in parallel. The
backend keeps the running totals for each model (elapsed time, per-category
counts, processed count, speed) and sends each model its own snapshot as soon
as it finishes a comment. The frontend just displays what it receives.
"""

import asyncio
import json
import time
from pathlib import Path

import websockets

from agent.config import settings
from agent.jev.service import classify_one as jev_classify
 
from agent.llm.service import CATEGORIES, classify_one as llm_classify


ROOT = Path(__file__).resolve().parent.parent
COMMENTS_FILE = ROOT / "youtube_comments.json"

HOST = "localhost"
PORT = 8765


def load_comments() -> list[str]:
    data = json.loads(COMMENTS_FILE.read_text(encoding="utf-8"))
    return [row["comment"] for row in data if row.get("comment")]


class ModelStats:
    """Running totals for one model."""

    def __init__(self, model: str):
        self.model = model
        self.counts = {category: 0 for category in CATEGORIES}
        self.processed = 0
        self.total_ms = 0.0

    def add(self, category: str | None, elapsed_ms: float) -> None:
        self.processed += 1
        self.total_ms += elapsed_ms
        if category in self.counts:
            self.counts[category] += 1

    def snapshot(self, total: int) -> dict:
        seconds = self.total_ms / 1000
        speed = self.processed / seconds if seconds > 0 else 0.0
        return {
            "type": "stats",
            "model": self.model,
            "processed": self.processed,
            "total": total,
            "time_seconds": round(seconds, 2),
            "speed": round(speed, 2),
            "counts": self.counts,
        }


def classify_safe(fn, comment: str) -> dict:
    """Run one model and measure how long it took. Never raises."""
    start = time.perf_counter()
    try:
        category = fn(comment)
        error = None
    except Exception as exc:
        category = None
        error = f"{type(exc).__name__}: {exc}"
    elapsed_ms = (time.perf_counter() - start) * 1000
    return {"category": category, "error": error, "elapsed_ms": elapsed_ms}


async def run_model(websocket, model: str, fn, comments: list[str], total: int):
    """Process the whole comment list for ONE model, at its own pace.

    Each classification runs in a thread (so it doesn't block the event loop)
    and its result is sent to the frontend as soon as it is done. This loop is
    independent from the other model, so a faster model races ahead.
    """
    stats = ModelStats(model)

    for comment in comments:
        result = await asyncio.to_thread(classify_safe, fn, comment)
        stats.add(result["category"], result["elapsed_ms"])
        await websocket.send(json.dumps(stats.snapshot(total)))


async def process(websocket):
    comments = load_comments()
    total = len(comments)

    await websocket.send(json.dumps({"type": "start", "total": total}))

    # Two independent pipelines running at the same time.
    await asyncio.gather(
        run_model(websocket, "jev", jev_classify, comments, total),
        run_model(
            websocket,
            "llm",
            lambda c: llm_classify(c, settings.LLM_PROVIDER),
            comments,
            total,
        ),
    )

    await websocket.send(json.dumps({"type": "done", "total": total}))


async def handler(websocket):
    try:
        async for message in websocket:
            data = json.loads(message)
            if data.get("action") == "start":
                await process(websocket)
    except websockets.ConnectionClosed:
        pass


async def main():
    print(f"WebSocket server running at ws://{HOST}:{PORT}")
    async with websockets.serve(handler, HOST, PORT):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
