"""Lowvyn remote MCP toolset wiring for DealScout."""

from __future__ import annotations

from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

from dealscout_agent.config import Settings

# Expose only the deal-finding surface; leave room to add forum scrapers later.
LOWVYN_TOOL_FILTER = [
    "intent_search",
    "search_products",
    "get_product",
    "verify_deal",
    "find_cheaper",
    "get_price_history",
    "get_retailers",
    "get_categories",
]


def build_lowvyn_toolset(settings: Settings) -> McpToolset:
    """Create a synchronous McpToolset pointed at Lowvyn's streamable HTTP MCP.

    ADK requires McpToolset to be defined synchronously in agent.py for
    production-compatible runners (`adk web` / `adk run`).
    """
    return McpToolset(
        connection_params=StreamableHTTPConnectionParams(
            url=settings.lowvyn_mcp_url,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "User-Agent": f"{settings.openrouter_app_name}/0.1",
            },
            timeout=30,
            sse_read_timeout=300,
        ),
        tool_filter=LOWVYN_TOOL_FILTER,
    )
