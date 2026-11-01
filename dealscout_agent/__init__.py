"""DealScout ADK agent package.

ADK discovers `root_agent` from this package when you run:

    adk run dealscout_agent
    adk web
"""

from dealscout_agent.agent import root_agent

__all__ = ["root_agent"]
