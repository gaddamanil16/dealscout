# Extending deal sources

DealScout currently uses **Lowvyn MCP** for Canadian retailer price intelligence.
More sources (deal forums, alert sites, historical trackers) can be added later
without changing the single-agent shape.

## Recommended pattern

1. Create a new module under `dealscout_agent/tools/`, e.g. `forums_mcp.py` or
   `slickdeals_client.py`.
2. Expose it as an ADK `McpToolset` or as pure Python tools that return the same
   JSON envelope used by local tools:

   ```json
   {
     "status": "success",
     "tool": "source_name",
     "data": {},
     "error": null
   }
   ```

3. Register the toolset in `dealscout_agent/agent.py` next to `lowvyn_toolset`.
4. Update the `find-best-deal` skill references so the agent knows when to call
   the new source.
5. Map foreign results into `DealCandidate`-compatible objects before
   `rank_deal_candidates`.

## Candidate future sources

| Source | Transport idea | Notes |
|--------|----------------|-------|
| Reddit deal subs | MCP or HTTP API | Noisy; needs trust scoring |
| Slickdeals / similar forums | Scraper MCP | ToS / rate limits |
| CamelCamelCamel / Keepa | API | History-focused |
| US retailers | New MCP/API | Separate currency + region |

## Ranking across sources

Keep ranking in `rank_deal_candidates` (or a future `rank_multi_source` tool)
so provenance is explicit via `sources_used` in `build_deal_report`.
