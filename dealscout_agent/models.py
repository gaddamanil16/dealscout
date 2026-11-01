"""Model factory for OpenRouter and local Ollama Gemma."""

from __future__ import annotations

from typing import Any

from google.adk.models.lite_llm import LiteLlm

from dealscout_agent.config import Settings


def build_model(settings: Settings) -> Any:
    """Build the ADK model object for the configured provider.

    - ``openrouter``: LiteLLM → OpenRouter free (or pinned) model
    - ``ollama`` + Gemma 3: ``Gemma3Ollama`` (ADK tool-calling workarounds)
    - ``ollama`` + Gemma 4 / other: ``LiteLlm`` with ``ollama_chat/...``
    """
    if settings.model_provider == "openrouter":
        return LiteLlm(model=settings.litellm_model)

    # Local Ollama path for offline / local testing.
    if settings.uses_local_gemma3:
        from google.adk.models import Gemma3Ollama

        # Gemma3Ollama defaults to ollama/gemma3:12b; prefer ollama_chat for ADK.
        model_id = settings.litellm_model
        if model_id.startswith("ollama/"):
            model_id = "ollama_chat/" + model_id.removeprefix("ollama/")
        return Gemma3Ollama(model=model_id, api_base=settings.ollama_api_base)

    return LiteLlm(
        model=settings.litellm_model,
        api_base=settings.ollama_api_base,
    )
