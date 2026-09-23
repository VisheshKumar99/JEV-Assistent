# JEV-Assistent

A live dashboard that classifies YouTube comments with **two different kinds of
models side by side** and races them in real time:

- **JEV** — a typed *decision* model (TypeSafe's Jev, via OpenRouter) that
  returns a calibrated probability distribution over allowed answers instead of
  generating text.
- **LLM** — a conventional chat model (OpenAI or a local Ollama model, through
  LangChain) that is prompted to reply with a single category name.

Both models receive the exact same comments in parallel. The browser shows, per
model, how many comments were processed, elapsed time, comments/sec, and a live
per-category bubble chart (each category is a circle that grows with its count).

---

## Why two model types?

A normal LLM classifier generates the category as text. If you ask it for a
confidence value, it *writes* "91%" — but the probability of emitting those
characters is not the probability that the label is correct. You also pay for
token generation just to get a label.

A **decision model** like Jev makes the predictive distribution itself the
output: it scores the allowed answers directly (e.g. `Praise: 0.80`,
`Criticism: 0.20`) and your application code decides what to do with those
numbers. This project exists to *feel* that difference — same inputs, two
philosophies, running next to each other.

### Background on Jev (decision-model concepts)

The design ideas below are paraphrased from [Bijit Ghosh, "Inside Jev,
Architecture of a Decision Model" (Medium)](https://medium.com/@bijit211987).
TypeSafe has not published Jev's exact architecture or training recipe, so this
is a plausible reconstruction, not an official spec. *Content was rephrased for
compliance with licensing restrictions.*

- **Encode once.** A causal transformer builds a representation of the shared
  context (the comment) without generating tokens.
- **Answer in parallel.** Each question is an isolated branch that reads the
  shared context plus its own options. An attention mask keeps sibling questions
  from seeing each other, so multiple typed questions can be answered together.
- **Direct readouts.** The model reads probabilities for the allowed answers
  straight from hidden state; there is no autoregressive decoding loop, which is
  part of why decision calls can be fast.
- **Calibration is the goal.** Jev's training method (RLCD — Reinforcement
  Learning for Calibrated Decisions) aims for *calibrated* probabilities: across
  all predictions scored at 80%, roughly 80% should turn out correct.
- **Verify on your own data.** Reordering or adding choices can shift results,
  and reported calibration numbers may not transfer to your workflow. Log
  predictions next to outcomes and measure before trusting automation.

Practical takeaway used by this project: because Jev returns a category choice
(and, more generally, calibrated probabilities), you can drive
threshold-based automation from it rather than parsing free-form model text.

---

## Architecture

```
                         youtube_comments.json
                                  │
                                  ▼
                        backend/server.py  (WebSocket, ws://localhost:8765)
                          │                         │
             per comment  │                         │  per comment
                          ▼                         ▼
                  agent/jev/service.py       agent/llm/service.py
                          │                         │
              agent/jev/decision_api.py     agent/llm/client.py
                 (OpenRouter Jev)                    │
                                            agent/llm/factory.py
                                             │               │
                              agent/llm/models/openai.py   .../ollama.py
                                     (OpenAI)                (Ollama)

        backend streams "stats" snapshots  ──────►  frontend/ (Vite + React)
                                                     App.jsx + ModelPanel.jsx
                                                     live bubble dashboard
```

### Python packages (`agent/`)

| Path | Role |
| --- | --- |
| `agent/config.py` | Loads all settings from `.env` into a `Settings` object. |
| `agent/llm/factory.py` | Picks the LLM provider (`openai` or `ollama`). |
| `agent/llm/models/openai.py` | Builds a LangChain `ChatOpenAI` client. |
| `agent/llm/models/ollama.py` | Builds a LangChain `ChatOllama` client. |
| `agent/llm/client.py` | `ask_llm(prompt)` — invokes the selected model. |
| `agent/llm/prompts.py` | The single-category classification prompt. |
| `agent/llm/service.py` | `classify_one()` + `normalize_category()`; owns the shared `CATEGORIES` list. |
| `agent/jev/decision_api.py` | `classify_youtube_comment()` — calls the Jev decision endpoint on OpenRouter. |
| `agent/jev/service.py` | `classify_one()` — thin wrapper so JEV matches the LLM contract (comment → category). |
| `agent/dataset/extract.py` | Builds `youtube_comments.json` from a Hugging Face dataset. |
| `agent/main.py`, `agent/jev/main.py` | Tiny manual smoke tests for each path. |

### Backend

- `backend/server.py` — WebSocket server. For every comment it runs JEV and the
  LLM in parallel (each in its own thread so a faster model races ahead), keeps
  running per-model totals, and pushes a `stats` snapshot after each comment.

Message contract sent to the frontend:

```jsonc
{ "type": "start", "total": 100 }
{ "type": "stats", "model": "jev"|"llm", "processed": 3, "total": 100,
  "time_seconds": 0.58, "speed": 1.7, "counts": { "Praise": 2, ... } }
{ "type": "done", "total": 100 }
```

### Frontend (`frontend/`)

- Vite + React app.
- `App.jsx` opens the WebSocket, sends `{ "action": "start" }`, and stores each
  snapshot in state.
- `ModelPanel.jsx` renders one model: the top stats row plus a bubble grid where
  each category is a circle whose radius scales with its count (area-proportional
  `sqrt` scaling), animating as data streams in.

### The 10 categories

`Praise`, `Criticism`, `Question`, `Suggestion`, `Spam / Promotion`,
`Toxicity`, `Humor`, `Personal Story`, `Technical Issue`, `Other`.

The list is defined once in `agent/llm/service.py` and mirrored in
`frontend/src/App.jsx`.

---

## Setup

### 1. Python dependencies

Run everything from the repository root so the `agent` and `backend` packages
resolve.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### 2. Configure `.env`

Secrets live only in `.env` (already git-ignored — do not commit it).

```dotenv
# Which LLM the UI races against JEV: "openai" or "ollama"
LLM_PROVIDER=openai

# JEV (decision model) via OpenRouter
OPENROUTER_API_KEY=your-openrouter-key

# OpenAI provider
OPENAI_API_KEY=your-openai-key
OPENAI_MODEL=gpt-4o-mini

# Ollama provider (local)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:3b
```

- `OPENROUTER_API_KEY` is required for the JEV path.
- `OPENAI_API_KEY` is required only when `LLM_PROVIDER=openai`.
- Ollama runs locally and needs no API key.

> Security note: `.env` in this repo contains live-looking keys. Keep it
> git-ignored and rotate any key that has been shared or committed.

### 3. (Optional) Regenerate the comment dataset

`youtube_comments.json` ships with 100 sample comments. To rebuild it from the
Hugging Face source:

```bash
python -m agent.dataset.extract
```

### 4. (Optional) Start Ollama for the local provider

Only needed when `LLM_PROVIDER=ollama`. Install Ollama separately, then in a
dedicated terminal:

```bash
ollama serve
ollama pull qwen2.5:3b
```

---

## Run the live dashboard

### Everything at once

From the repository root, this starts the backend and the React frontend and
stops both on Ctrl+C:

```bash
python run.py
```

Then open `http://localhost:5173` and click **Start Process**.

### Run each part manually

Backend:

```bash
.venv/bin/python -m backend.server   # ws://localhost:8765
```

Frontend:

```bash
cd frontend
npm install
npm run dev                           # http://localhost:5173
```

---

## Quick manual checks

Classify a single comment with each path (uses your `.env` settings):

```bash
python -m agent.main       # LLM (OpenAI/Ollama)
python -m agent.jev.main   # JEV (OpenRouter decision model)
```

---

## Attribution

Jev architecture background is paraphrased and summarized from Bijit Ghosh,
*"Inside Jev, Architecture of a Decision Model"* on Medium. All rephrasing is the
author's; see the [original article](https://medium.com/@bijit211987) for the
full discussion.
