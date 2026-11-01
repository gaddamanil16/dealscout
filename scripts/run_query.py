#!/usr/bin/env python3
"""One-shot CLI runner for DealScout outside `adk run` / `adk web`."""

from __future__ import annotations

import argparse
import asyncio
import sys
from uuid import uuid4

from dotenv import load_dotenv

load_dotenv()


async def _run(query: str) -> str:
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types

    from dealscout_agent.agent import root_agent

    app_name = "dealscout"
    user_id = "cli-user"
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=str(uuid4()),
    )
    runner = Runner(agent=root_agent, app_name=app_name, session_service=session_service)

    final_text = ""
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session.id,
        new_message=types.Content(role="user", parts=[types.Part(text=query)]),
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if getattr(part, "text", None):
                    final_text = part.text
        if getattr(event, "is_final_response", None) and event.is_final_response():
            break

    return final_text or "(No final text response from agent.)"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a DealScout shopping query.")
    parser.add_argument(
        "query",
        nargs="?",
        default="find me best deal for 75 inch TV",
        help="Natural language deal request",
    )
    args = parser.parse_args(argv)

    try:
        result = asyncio.run(_run(args.query))
    except ValueError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001
        print(f"Run failed: {exc}", file=sys.stderr)
        return 1

    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
