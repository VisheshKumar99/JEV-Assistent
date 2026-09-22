# JEV-Assistent

## Run the LLM demo

This project supports both a local Ollama model and OpenAI through LangChain. The provider modules are loaded from the `agent` package, so run commands from the repository root.

### 1. Install Python dependencies

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### 2. Configure `.env`

Keep secrets only in the local `.env` file. Do not commit it.

```dotenv
LLM_PROVIDER=both
LLM_MAX_CONCURRENCY=4
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:3b
OPENAI_MODEL=gpt-4o-mini
OPENAI_API_KEY=your-openai-api-key
```

`LLM_PROVIDER` accepts `ollama`, `openai`, or `both`. `both` runs the two providers concurrently for the same comment batch. `LLM_MAX_CONCURRENCY` bounds in-flight requests inside each provider, which is important for large comment streams.

`OPENAI_API_KEY` is required only when running the OpenAI provider. Ollama uses its local service and does not need an API key.

### 3. Start Ollama when using the local provider

Install Ollama separately, start the Ollama service, and pull the configured model:

```bash
ollama serve
ollama pull qwen2.5:3b
```

Run this in a separate terminal because `ollama serve` stays running.

### 4. Run the sample

```bash
python -m agent.main
```

The sample sends one comment to Ollama and then OpenAI. The benchmark integration will later run both providers in parallel over bounded batches.
