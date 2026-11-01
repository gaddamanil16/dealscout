"""Tests for model provider configuration and factory."""

from __future__ import annotations

import os

import pytest
from google.adk.models.lite_llm import LiteLlm

# Satisfy package import of root_agent before provider-specific tests run.
os.environ.setdefault("OPENROUTER_API_KEY", "test-key")

from dealscout_agent.config import get_settings  # noqa: E402
from dealscout_agent.models import build_model  # noqa: E402


@pytest.fixture(autouse=True)
def _reset_provider_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    for key in (
        "DEALSCOUT_MODEL_PROVIDER",
        "OPENROUTER_MODEL",
        "OLLAMA_API_BASE",
        "OLLAMA_MODEL",
    ):
        monkeypatch.delenv(key, raising=False)


def test_openrouter_requires_api_key(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DEALSCOUT_MODEL_PROVIDER", "openrouter")
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    with pytest.raises(ValueError, match="OPENROUTER_API_KEY"):
        get_settings()


def test_openrouter_model_prefix(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DEALSCOUT_MODEL_PROVIDER", "openrouter")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setenv("OPENROUTER_MODEL", "openrouter/free")
    settings = get_settings()
    assert settings.litellm_model == "openrouter/free"

    monkeypatch.setenv("OPENROUTER_MODEL", "google/gemma-4-31b-it:free")
    settings = get_settings()
    assert settings.litellm_model == "openrouter/google/gemma-4-31b-it:free"
    model = build_model(settings)
    assert isinstance(model, LiteLlm)


def test_ollama_alias_local(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DEALSCOUT_MODEL_PROVIDER", "local")
    monkeypatch.setenv("OLLAMA_MODEL", "gemma3:12b")
    settings = get_settings()
    assert settings.model_provider == "ollama"
    assert settings.uses_local_gemma3 is True
    assert settings.litellm_model == "ollama_chat/gemma3:12b"


def test_build_gemma3_ollama_model(monkeypatch: pytest.MonkeyPatch):
    from google.adk.models import Gemma3Ollama

    monkeypatch.setenv("DEALSCOUT_MODEL_PROVIDER", "ollama")
    monkeypatch.setenv("OLLAMA_MODEL", "gemma3:12b")
    monkeypatch.setenv("OLLAMA_API_BASE", "http://127.0.0.1:11434")
    settings = get_settings()
    model = build_model(settings)
    assert isinstance(model, Gemma3Ollama)


def test_build_gemma4_uses_litellm(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DEALSCOUT_MODEL_PROVIDER", "ollama")
    monkeypatch.setenv("OLLAMA_MODEL", "gemma4:e4b")
    settings = get_settings()
    assert settings.uses_local_gemma3 is False
    model = build_model(settings)
    assert isinstance(model, LiteLlm)
