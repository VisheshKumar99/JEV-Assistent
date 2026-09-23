"""Start the backend WebSocket server and the React frontend together.

Usage:
    python run.py

Press Ctrl+C to stop both. This uses the project's virtualenv Python for the
backend and npm for the frontend.
"""

import os
import signal
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FRONTEND = ROOT / "frontend"

# Prefer the project's virtualenv Python; fall back to the current interpreter.
VENV_PYTHON = ROOT / ".venv" / "bin" / "python"
PYTHON = str(VENV_PYTHON) if VENV_PYTHON.exists() else sys.executable


def start_backend() -> subprocess.Popen:
    print("Starting backend  -> ws://localhost:8765")
    return subprocess.Popen([PYTHON, "-m", "backend.dummy_server"], cwd=ROOT)


def start_frontend() -> subprocess.Popen:
    if not (FRONTEND / "node_modules").exists():
        print("Installing frontend dependencies (first run)...")
        subprocess.run(["npm", "install"], cwd=FRONTEND, check=True)

    print("Starting frontend -> http://localhost:5173")
    return subprocess.Popen(["npm", "run", "dev"], cwd=FRONTEND)


def main() -> None:
    backend = start_backend()
    frontend = start_frontend()
    processes = [backend, frontend]

    def shutdown(*_):
        print("\nStopping...")
        for proc in processes:
            if proc.poll() is None:
                proc.terminate()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # If either process exits on its own, stop the other one too.
    try:
        while True:
            for proc in processes:
                if proc.poll() is not None:
                    print(f"\nA process exited (code {proc.returncode}). Shutting down.")
                    shutdown()
            try:
                backend.wait(timeout=1)
            except subprocess.TimeoutExpired:
                pass
    except KeyboardInterrupt:
        shutdown()


if __name__ == "__main__":
    main()
