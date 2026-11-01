# DealScout

Single-agent shopping deal finder built with **Google ADK**, **OpenRouter free models**, and the **Lowvyn MCP** price-intelligence server.

Ask things like:

> find me best deal for 75 inch TV

The agent loads ADK skills on demand, calls Lowvyn tools for live Canadian retailer data, and keeps custom tool returns as structured JSON.

## Features

- One `root_agent` (no multi-agent complexity)
- OpenRouter free model via LiteLLM (`openrouter/openrouter/free` by default)
- Lowvyn MCP tool calling (`intent_search`, `verify_deal`, `find_cheaper`, …)
- ADK Skills: `find-best-deal`, `compare-and-verify`
- Local tools with consistent JSON envelopes + `deal_report_v1` schema
- Extension path for future forum / scraper sources

## Project layout

```text
dealscout/
├── dealscout_agent/
│   ├── agent.py              # root_agent definition
│   ├── config.py             # env settings
│   ├── prompts.py            # system instruction
│   ├── tools/
│   │   ├── lowvyn_mcp.py     # remote MCP toolset
│   │   ├── local_tools.py    # structured JSON helpers
│   │   └── schemas.py        # pydantic models / envelopes
│   └── skills/
│       ├── find-best-deal/
│       └── compare-and-verify/
├── docs/
│   ├── architecture.md
│   ├── setup.md
│   └── extending-deal-sources.md
├── scripts/run_query.py
├── pyproject.toml
├── uv.lock
└── tests/
```

## Quick start

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv sync
cp .env.example .env   # set OPENROUTER_API_KEY (or use local Gemma below)

uv run adk run dealscout_agent
# or
uv run python scripts/run_query.py "find me best deal for 75 inch TV"
```

### Local Gemma (Ollama)

```bash
ollama pull gemma3:12b
# in .env:
# DEALSCOUT_MODEL_PROVIDER=ollama
# OLLAMA_MODEL=gemma3:12b

uv run adk run dealscout_agent
```

Full setup notes: [docs/setup.md](docs/setup.md)  
Architecture: [docs/architecture.md](docs/architecture.md)

## Structured tool returns

Local tools always return:

```json
{
  "status": "success",
  "tool": "parse_deal_query",
  "data": { "...": "..." },
  "error": null
}
```

The final recommendation is normalized through `build_deal_report` into
`deal_report_v1` (see `dealscout_agent/skills/find-best-deal/assets/deal-response.schema.json`).

## Current coverage

Lowvyn tracks Canadian retailers (CAD): Amazon.ca, Walmart.ca, BestBuy.ca,
Canadian Tire, Canada Computers, Newegg.ca, Visions.ca.

Forum scraping and additional deal boards are intentionally deferred — see
[docs/extending-deal-sources.md](docs/extending-deal-sources.md).
