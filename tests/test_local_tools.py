"""Unit tests for structured JSON local tools."""

from __future__ import annotations

import json
import os

import pytest

# Ensure settings load without a real key during unit tests.
os.environ.setdefault("OPENROUTER_API_KEY", "test-key")
os.environ.setdefault("DEALSCOUT_CURRENCY", "CAD")

from dealscout_agent.tools.local_tools import (  # noqa: E402
    build_deal_report,
    parse_deal_query,
    rank_deal_candidates,
)


def test_parse_deal_query_extracts_size_and_product():
    result = parse_deal_query("find me best deal for 75 inch TV")
    assert result["status"] == "success"
    assert result["tool"] == "parse_deal_query"
    assert "75" in result["data"]["product"]
    assert "TV" in result["data"]["product"].upper() or "tv" in result["data"]["search_query"].lower()
    assert result["data"]["currency"] == "CAD"
    assert result["error"] is None


def test_parse_deal_query_rejects_empty():
    result = parse_deal_query("  ")
    assert result["status"] == "error"
    assert result["error"]["code"] == "empty_query"


def test_rank_and_build_report_roundtrip():
    candidates = [
        {
            "title": "Samsung 75 inch TV",
            "price": 999.0,
            "retailer": "BestBuy.ca",
            "score": 88,
            "dealVerdict": "real_deal",
            "url": "https://example.test/a",
        },
        {
            "title": "Generic 75 inch TV",
            "price": 899.0,
            "retailer": "Amazon.ca",
            "score": 40,
            "dealVerdict": "average",
            "url": "https://example.test/b",
        },
    ]
    ranked = rank_deal_candidates(json.dumps(candidates), max_results=2)
    assert ranked["status"] == "success"
    assert ranked["data"]["count"] == 2
    assert ranked["data"]["ranked_deals"][0]["title"].startswith("Samsung")

    report = build_deal_report(
        query="75 inch TV",
        ranked_deals_json=json.dumps(ranked["data"]["ranked_deals"]),
        summary="Samsung wins on deal quality despite a slightly higher price.",
        caveats_json=json.dumps(["Canadian retailers only via Lowvyn"]),
        sources_used_json=json.dumps(["lowvyn"]),
    )
    assert report["status"] == "success"
    payload = report["data"]["report"]
    assert payload["response_format"] == "deal_report_v1"
    assert payload["best_deal"]["rank"] == 1
    assert payload["sources_used"] == ["lowvyn"]


def test_rank_invalid_json():
    result = rank_deal_candidates("{not-json")
    assert result["status"] == "error"
    assert result["error"]["code"] == "invalid_json"


if __name__ == "__main__":
    pytest.main([__file__])
