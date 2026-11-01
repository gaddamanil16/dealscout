# Setup

## Prerequisites

- [uv](https://docs.astral.sh/uv/) (install via `brew install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Python 3.11+ (uv can install it for you)
- **OpenRouter mode:** an [OpenRouter](https://openrouter.ai/keys) API key
- **Local Gemma mode:** [Ollama](https://ollama.com/) with a Gemma model pulled
- Network access to `https://api.lowvyn.com/mcp` (and OpenRouter when not local)

## Install

```bash
cd dealscout
uv sync
```

This creates `.venv`, installs runtime + dev dependencies from `pyproject.toml`,
and uses the locked versions in `uv.lock`.

Useful variants:

```bash
uv sync                 # default: includes the `dev` group
uv sync --no-dev        # runtime deps only
uv lock                 # refresh the lockfile after dependency edits
uv add <package>        # add a runtime dependency
uv add --dev <package>  # add a dev dependency
```

## Configure

```bash
cp .env.example .env
# edit .env — set OPENROUTER_API_KEY, or switch to local Gemma (below)
```

### Local Gemma testing (Ollama)

No OpenRouter key needed. Pull a model, then point DealScout at Ollama:

```bash
ollama pull gemma3:12b

# in .env
DEALSCOUT_MODEL_PROVIDER=ollama
OLLAMA_API_BASE=http://localhost:11434
OLLAMA_MODEL=gemma3:12b
```

Gemma 3 uses ADK's `Gemma3Ollama` (tool-calling workarounds). For Gemma 4:

```bash
ollama pull gemma4
# OLLAMA_MODEL=gemma4
```

Then run as usual with `uv run …`.

Optional knobs:

| Variable | Default | Purpose |
|----------|---------|---------|
| `DEALSCOUT_MODEL_PROVIDER` | `openrouter` | `openrouter` or `ollama` (`local` also accepted) |
| `OPENROUTER_MODEL` | `openrouter/openrouter/free` | Free router that picks a tool-capable free model |
| `OLLAMA_API_BASE` | `http://localhost:11434` | Local Ollama server URL |
| `OLLAMA_MODEL` | `gemma3:12b` | Ollama tag (e.g. `gemma3:12b`, `gemma4`) |
| `LOWVYN_MCP_URL` | `https://api.lowvyn.com/mcp` | Lowvyn MCP endpoint |
| `DEALSCOUT_MAX_RESULTS` | `5` | Preferred ranked result count |
| `DEALSCOUT_CURRENCY` | `CAD` | Display/report currency |

## Run

Prefer `uv run` so the project environment is used automatically (no manual
`source .venv/bin/activate` required).

Interactive ADK CLI:

```bash
uv run adk run dealscout_agent
```

ADK web UI (run from the project root):

```bash
uv run adk web --port 8000
```

One-shot query:

```bash
uv run python scripts/run_query.py "find me best deal for 75 inch TV"
# or, after sync:
uv run dealscout "find me best deal for 75 inch TV"
```

## Tests

```bash
uv run pytest -q
```

## Notes

- Lowvyn is free/read-only and needs no API key.
- OpenRouter free models are rate-limited; if tool calling flakes, pin a specific
  free tool-capable model in `OPENROUTER_MODEL` (for example a `:free` model that
  advertises tools support on OpenRouter).
- Local Gemma still calls Lowvyn over the network for deal data; only the LLM
  runs on your machine.
- Prefer Ollama models with tool support for reliable agent behavior.
- ADK Web is for local development only.
- Commit `uv.lock` so installs stay reproducible.
