# Architecture

DealScout is a **single-agent** application built with [Google ADK](https://adk.dev/).

```text
User query
    │
    ▼
┌──────────────────────────────────────────────┐
│              DealScout root_agent            │
│  Model: OpenRouter (LiteLLM) or local Gemma  │
│         via Ollama (Gemma3Ollama / LiteLlm)  │
│  Skills: find-best-deal, compare-and-verify  │
└───────────────┬───────────────┬──────────────┘
                │               │
                ▼               ▼
     Local JSON tools     Lowvyn MCP toolset
  parse_deal_query        intent_search
  rank_deal_candidates    search_products
  build_deal_report       verify_deal / find_cheaper
                │               │
                └───────┬───────┘
                        ▼
              Structured deal_report_v1
                        │
                        ▼
                 User-facing answer
```

## Components

| Piece | Role |
|-------|------|
| `dealscout_agent/agent.py` | Defines `root_agent` for `adk run` / `adk web` |
| `dealscout_agent/models.py` | Provider switch: OpenRouter vs local Ollama Gemma |
| OpenRouter + LiteLLM | Default cloud free-model inference with tool calling |
| Ollama Gemma | Optional local testing (`DEALSCOUT_MODEL_PROVIDER=ollama`) |
| ADK Skills | On-demand workflows that keep the context window lean |
| Lowvyn MCP | Live Canadian retailer price intelligence |
| Local tools | Deterministic structured JSON parse/rank/report helpers |

## Why this shape

- **One agent** keeps the first version simple and easy to reason about.
- **Skills** hold lengthy deal-finding instructions so they load only when needed.
- **MCP** connects Lowvyn without custom scraper code.
- **Local tools return JSON envelopes** so ranking and final reports are schema-stable.

## Extension point

Additional deal sources (forums, Reddit, Slickdeals, camelcamelcamel, etc.) should
be added as new toolsets beside Lowvyn — see [extending-deal-sources.md](./extending-deal-sources.md).
