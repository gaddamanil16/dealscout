"""Local DealScout tools with structured JSON returns.

These complement Lowvyn MCP tools: they normalize intent, rank candidates,
and emit a final deal report as validated JSON.
"""

from __future__ import annotations

import json
import re
from typing import Any

from dealscout_agent.config import get_settings
from dealscout_agent.tools.schemas import (
    DealCandidate,
    DealReport,
    ParsedDealQuery,
    RankedDeal,
    error,
    partial,
    success,
)


_SIZE_RE = re.compile(r"(\d{2,3})\s*[\"']?\s*(?:inch|in)?", re.IGNORECASE)
_PRICE_RE = re.compile(
    r"(?:under|below|max(?:imum)?|budget(?:\s+of)?|less\s+than)\s*\$?\s*([\d,]+(?:\.\d+)?)",
    re.IGNORECASE,
)
_BRAND_HINTS = (
    "samsung",
    "lg",
    "sony",
    "tcl",
    "hisense",
    "vizio",
    "apple",
    "dell",
    "hp",
    "lenovo",
    "asus",
    "bose",
    "dyson",
)


def parse_deal_query(user_query: str) -> dict[str, Any]:
    """Parse a free-text shopping request into structured search parameters.

    Args:
        user_query: Natural language deal request, e.g. "find me best deal for 75 inch TV".

    Returns:
        JSON envelope with ParsedDealQuery fields under ``data``.
    """
    tool = "parse_deal_query"
    try:
        settings = get_settings()
        text = (user_query or "").strip()
        if not text:
            return error(tool, "empty_query", "user_query must be a non-empty string")

        lowered = text.lower()
        brand = next((b for b in _BRAND_HINTS if b in lowered), None)

        max_price = None
        price_match = _PRICE_RE.search(text)
        if price_match:
            max_price = float(price_match.group(1).replace(",", ""))

        size_match = _SIZE_RE.search(text)
        size_token = f"{size_match.group(1)} inch" if size_match else None

        # Lightweight product heuristic: strip filler words.
        filler = {
            "find",
            "me",
            "the",
            "best",
            "deal",
            "deals",
            "for",
            "a",
            "an",
            "please",
            "looking",
            "want",
            "need",
            "cheap",
            "cheapest",
            "good",
            "price",
        }
        tokens = [t for t in re.findall(r"[A-Za-z0-9+\-.\"]+", text) if t.lower() not in filler]
        product = " ".join(tokens) if tokens else text
        if size_token and size_token.lower() not in product.lower():
            product = f"{size_token} {product}".strip()

        search_parts = [product]
        if brand and brand not in product.lower():
            search_parts.insert(0, brand)
        if max_price is not None:
            search_parts.append(f"under {max_price}")

        parsed = ParsedDealQuery(
            product=product,
            category=None,
            brand=brand.title() if brand else None,
            max_price=max_price,
            min_price=None,
            currency=settings.currency,
            must_have=[size_token] if size_token else [],
            nice_to_have=[],
            retailer_preference=None,
            search_query=" ".join(search_parts),
        )
        return success(tool, parsed.model_dump(mode="json"))
    except Exception as exc:  # noqa: BLE001 - surface as structured tool error
        return error(tool, "parse_failed", str(exc))


def rank_deal_candidates(
    candidates_json: str,
    max_results: int = 5,
    prefer_verdict: str = "real_deal",
) -> dict[str, Any]:
    """Rank deal candidates and return a structured ordered list.

    Args:
        candidates_json: JSON array (or object with ``items``/``products``) of candidates.
        max_results: Maximum ranked deals to return.
        prefer_verdict: Preferred Lowvyn deal verdict boost (e.g. real_deal).

    Returns:
        JSON envelope with ``ranked_deals`` and ranking metadata.
    """
    tool = "rank_deal_candidates"
    try:
        raw = json.loads(candidates_json) if isinstance(candidates_json, str) else candidates_json
        if isinstance(raw, dict):
            items = raw.get("items") or raw.get("products") or raw.get("results") or raw.get("data")
            if items is None and any(k in raw for k in ("title", "price", "name")):
                items = [raw]
            elif items is None:
                items = []
        elif isinstance(raw, list):
            items = raw
        else:
            return error(tool, "invalid_input", "candidates_json must be a JSON array or object")

        if not items:
            return partial(
                tool,
                {"ranked_deals": [], "count": 0},
                "No candidates provided to rank",
            )

        verdict_boost = {
            "real_deal": 40,
            "modest_deal": 25,
            "average": 10,
            "bad_time": -20,
            "insufficient_data": 0,
        }

        scored: list[tuple[float, DealCandidate]] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            candidate = DealCandidate(
                title=str(item.get("title") or item.get("name") or "Unknown product"),
                price=_as_float(item.get("price") or item.get("currentPrice")),
                currency=str(item.get("currency") or "CAD"),
                retailer=item.get("retailer") or item.get("store"),
                url=item.get("url") or item.get("canonicalUrl") or item.get("productUrl"),
                lowvyn_id=item.get("id") or item.get("lowvyn_id") or item.get("lowvynId"),
                lowvyn_score=_as_float(item.get("lowvyn_score") or item.get("score") or item.get("lowvynScore")),
                deal_verdict=item.get("deal_verdict") or item.get("dealVerdict") or item.get("verdict"),
                savings=_as_float(item.get("savings")),
                notes=item.get("notes") or item.get("explanation"),
            )
            score = 0.0
            if candidate.lowvyn_score is not None:
                score += float(candidate.lowvyn_score)
            if candidate.deal_verdict:
                score += verdict_boost.get(str(candidate.deal_verdict).lower(), 0)
                if prefer_verdict and candidate.deal_verdict.lower() == prefer_verdict.lower():
                    score += 5
            if candidate.price is not None:
                # Mild preference for lower price when scores are similar.
                score += max(0.0, 20.0 - (candidate.price / 100.0))
            scored.append((score, candidate))

        scored.sort(key=lambda pair: pair[0], reverse=True)
        limit = max(1, min(int(max_results or 5), 20))
        ranked: list[RankedDeal] = []
        for idx, (score, candidate) in enumerate(scored[:limit], start=1):
            rationale_parts = [f"composite_score={round(score, 2)}"]
            if candidate.lowvyn_score is not None:
                rationale_parts.append(f"lowvyn_score={candidate.lowvyn_score}")
            if candidate.deal_verdict:
                rationale_parts.append(f"verdict={candidate.deal_verdict}")
            if candidate.price is not None:
                rationale_parts.append(f"price={candidate.price} {candidate.currency}")
            ranked.append(
                RankedDeal(
                    **candidate.model_dump(),
                    rank=idx,
                    rationale="; ".join(rationale_parts),
                )
            )

        return success(
            tool,
            {
                "ranked_deals": [d.model_dump(mode="json") for d in ranked],
                "count": len(ranked),
                "prefer_verdict": prefer_verdict,
            },
        )
    except json.JSONDecodeError as exc:
        return error(tool, "invalid_json", f"Could not parse candidates_json: {exc}")
    except Exception as exc:  # noqa: BLE001
        return error(tool, "rank_failed", str(exc))


def build_deal_report(
    query: str,
    ranked_deals_json: str,
    summary: str,
    caveats_json: str = "[]",
    sources_used_json: str = '["lowvyn"]',
) -> dict[str, Any]:
    """Build the final structured deal recommendation report.

    Args:
        query: Original user query.
        ranked_deals_json: JSON array of ranked deals (from rank_deal_candidates).
        summary: Short human-readable recommendation summary.
        caveats_json: JSON array of caveat strings.
        sources_used_json: JSON array of source identifiers (e.g. lowvyn).

    Returns:
        JSON envelope with a ``deal_report_v1`` payload under ``data.report``.
    """
    tool = "build_deal_report"
    try:
        settings = get_settings()
        ranked_raw = json.loads(ranked_deals_json)
        if isinstance(ranked_raw, dict):
            ranked_raw = ranked_raw.get("ranked_deals") or ranked_raw.get("data", {}).get(
                "ranked_deals", []
            )
        if not isinstance(ranked_raw, list):
            return error(tool, "invalid_ranked_deals", "ranked_deals_json must be a JSON array")

        caveats = json.loads(caveats_json) if caveats_json else []
        sources = json.loads(sources_used_json) if sources_used_json else ["lowvyn"]
        if not isinstance(caveats, list):
            caveats = [str(caveats)]
        if not isinstance(sources, list):
            sources = [str(sources)]

        ranked_models: list[RankedDeal] = []
        for item in ranked_raw:
            if not isinstance(item, dict):
                continue
            payload = dict(item)
            payload.setdefault("rank", len(ranked_models) + 1)
            payload.setdefault("rationale", "Selected from ranked candidates")
            ranked_models.append(RankedDeal.model_validate(payload))

        best = ranked_models[0] if ranked_models else None
        alternatives = ranked_models[1:] if len(ranked_models) > 1 else []

        report = DealReport(
            query=query,
            currency=settings.currency,
            best_deal=best,
            alternatives=alternatives,
            summary=summary or "No summary provided.",
            caveats=[str(c) for c in caveats],
            sources_used=[str(s) for s in sources],
        )
        return success(tool, {"report": report.model_dump(mode="json")})
    except json.JSONDecodeError as exc:
        return error(tool, "invalid_json", str(exc))
    except Exception as exc:  # noqa: BLE001
        return error(tool, "report_failed", str(exc))


def _as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
