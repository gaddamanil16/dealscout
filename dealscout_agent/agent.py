"""DealScout root agent — Google ADK + OpenRouter + Lowvyn MCP + Skills."""

from __future__ import annotations

import pathlib

from google.adk import Agent
from google.adk.skills import load_skill_from_dir
from google.adk.tools import skill_toolset

from dealscout_agent.config import apply_runtime_env
from dealscout_agent.models import build_model
from dealscout_agent.prompts import ROOT_INSTRUCTION
from dealscout_agent.tools import (
    build_deal_report,
    build_lowvyn_toolset,
    parse_deal_query,
    rank_deal_candidates,
)

_SETTINGS = apply_runtime_env()
_SKILLS_DIR = pathlib.Path(__file__).parent / "skills"

find_best_deal_skill = load_skill_from_dir(_SKILLS_DIR / "find-best-deal")
compare_and_verify_skill = load_skill_from_dir(_SKILLS_DIR / "compare-and-verify")

# SkillToolset.additional_tools are only exposed after a skill is activated.
# Register local helpers on the agent directly so they are always callable.
deal_skill_toolset = skill_toolset.SkillToolset(
    skills=[find_best_deal_skill, compare_and_verify_skill],
)

lowvyn_toolset = build_lowvyn_toolset(_SETTINGS)

root_agent = Agent(
    name="dealscout",
    model=build_model(_SETTINGS),
    description=(
        "Finds the best shopping deals for a user query using Lowvyn price "
        "intelligence and structured JSON analysis tools."
    ),
    instruction=ROOT_INSTRUCTION,
    tools=[
        deal_skill_toolset,
        lowvyn_toolset,
        parse_deal_query,
        rank_deal_candidates,
        build_deal_report,
    ],
)
