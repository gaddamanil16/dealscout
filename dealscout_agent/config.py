"""Runtime configuration for DealScout."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv

# Load .env from the agent package and the project root (if present).
_AGENT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _AGENT_DIR.parent
load_dotenv(_PROJECT_ROOT / ".env")
load_dotenv(_AGENT_DIR / ".env")

ModelProvider = Literal["openrouter", "ollama"]


@dataclass(frozen=True)
class Settings:
    """Immutable settings resolved from environment variables."""

    model_provider: ModelProvider
    openrouter_api_key: str
    openrouter_model: str
    openrouter_site_url: str
    openrouter_app_name: str
    ollama_api_base: str
    ollama_model: str
    lowvyn_mcp_url: str
    max_results: int
    currency: str

    @property
    def litellm_model(self) -> str:
        """Return the LiteLLM / ADK model string for the active provider."""
        if self.model_provider == "ollama":
            return self._ollama_litellm_model()
        model = self.openrouter_model
        if not model.startswith("openrouter/"):
            return f"openrouter/{model}"
        return model

    def _ollama_litellm_model(self) -> str:
        model = self.ollama_model.strip()
        if model.startswith(("ollama/", "ollama_chat/")):
            return model
        # Prefer ollama_chat to avoid infinite tool-call loops with ADK.
        return f"ollama_chat/{model}"

    @property
    def uses_local_gemma3(self) -> bool:
        """True when the configured Ollama model is a Gemma 3 variant."""
        if self.model_provider != "ollama":
            return False
        name = self.ollama_model.lower()
        # Gemma 4 tags must not match this path.
        if "gemma4" in name or "gemma-4" in name:
            return False
        return "gemma3" in name or "gemma-3" in name or name.split("/")[-1].startswith("gemma3")


def get_settings() -> Settings:
    """Load and validate application settings."""
    provider_raw = os.getenv("DEALSCOUT_MODEL_PROVIDER", "openrouter").strip().lower()
    if provider_raw in {"local", "gemma", "ollama_local"}:
        provider_raw = "ollama"
    if provider_raw not in {"openrouter", "ollama"}:
        raise ValueError(
            "DEALSCOUT_MODEL_PROVIDER must be 'openrouter' or 'ollama' "
            f"(got {provider_raw!r})"
        )
    provider: ModelProvider = provider_raw  # type: ignore[assignment]

    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if provider == "openrouter" and not api_key:
        raise ValueError(
            "OPENROUTER_API_KEY is required when DEALSCOUT_MODEL_PROVIDER=openrouter. "
            "Copy .env.example to .env and add your key, or set "
            "DEALSCOUT_MODEL_PROVIDER=ollama for local Gemma testing."
        )

    return Settings(
        model_provider=provider,
        openrouter_api_key=api_key,
        openrouter_model=os.getenv("OPENROUTER_MODEL", "openrouter/openrouter/free").strip(),
        openrouter_site_url=os.getenv("OPENROUTER_SITE_URL", "http://localhost").strip(),
        openrouter_app_name=os.getenv("OPENROUTER_APP_NAME", "dealscout").strip(),
        ollama_api_base=os.getenv("OLLAMA_API_BASE", "http://localhost:11434").strip(),
        ollama_model=os.getenv("OLLAMA_MODEL", "gemma3:12b").strip(),
        lowvyn_mcp_url=os.getenv("LOWVYN_MCP_URL", "https://api.lowvyn.com/mcp").strip(),
        max_results=int(os.getenv("DEALSCOUT_MAX_RESULTS", "5")),
        currency=os.getenv("DEALSCOUT_CURRENCY", "CAD").strip().upper(),
    )


def apply_runtime_env(settings: Settings | None = None) -> Settings:
    """Ensure provider-specific env vars are present for the process."""
    settings = settings or get_settings()

    if settings.model_provider == "openrouter":
        os.environ.setdefault("OPENROUTER_API_KEY", settings.openrouter_api_key)
        os.environ.setdefault("OR_SITE_URL", settings.openrouter_site_url)
        os.environ.setdefault("OR_APP_NAME", settings.openrouter_app_name)
    else:
        # LiteLLM / ADK Ollama integrations read this for non-generation calls.
        os.environ["OLLAMA_API_BASE"] = settings.ollama_api_base

    return settings
