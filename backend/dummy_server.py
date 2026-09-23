"""Dummy WebSocket server for frontend wiring.

Streams fake classification stats in the exact shape the frontend expects,
without calling any real model. Use this to verify the socket + UI update
loop end-to-end before hooking up the actual JEV/LLM classifiers.

Message contract (matches frontend/src/App.jsx):
    {"type": "start", "total": <int>}
    {"type": "stats", "model": "jev"|"llm", "processed", "total",
     "time_seconds", "speed", "counts": {<category>: <int>, ...}}
    {"type": "done", "total": <int>}

Run:
    python -m backend.dummy_server
"""

import asyncio
import json
import random

import websockets


HOST = "localhost"
PORT = 8765

# Same 10 categories the frontend renders.
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

# How many fake comments to "process".
TOTAL = 10

# Fake per-comment latency (seconds) for each model, so one races ahead.
MODEL_DELAY = {"jev": 0.15, "llm": 0.45}


class DummyStats:
    """Running totals for one model, filled with random categories."""

    def __init__(self, model: str):
        self.model = model
        self.counts = {category: 0 for category in CATEGORIES}
        self.processed = 0
        self.total_ms = 0.0

    def add(self, elapsed_ms: float) -> None:
        self.processed += 1
        self.total_ms += elapsed_ms
        category = random.choice(CATEGORIES)
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


async def run_model(websocket, model: str, total: int):
    """Emit one fake stats snapshot per comment, at this model's own pace."""
    stats = DummyStats(model)
    delay = MODEL_DELAY.get(model, 0.3)

    for _ in range(total):
        await asyncio.sleep(delay)
        # Add a little jitter so the numbers look real.
        elapsed_ms = delay * 1000 * random.uniform(0.8, 1.2)
        stats.add(elapsed_ms)
        await websocket.send(json.dumps(stats.snapshot(total)))


async def process(websocket):
    total = TOTAL

    await websocket.send(json.dumps({"type": "start", "total": total}))

    # Two independent pipelines running at the same time, like the real server.
    await asyncio.gather(
        run_model(websocket, "jev", total),
        run_model(websocket, "llm", total),
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
    print(f"Dummy WebSocket server running at ws://{HOST}:{PORT}")
    async with websockets.serve(handler, HOST, PORT):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
