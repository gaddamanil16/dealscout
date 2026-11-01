"""Structured JSON schemas for DealScout tool returns.

Every custom tool returns a dict that serializes cleanly to JSON with a
consistent envelope:

    {
      "status": "success" | "error" | "partial",
      "tool": "<tool_name>",
      "data": { ... },
      "error": null | { "code": "...", "message": "..." }
    }
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class ToolStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"


class ToolError(BaseModel):
    code: str
    message: str


class ToolEnvelope(BaseModel):
    """Canonical JSON envelope for all custom tool call returns."""

    status: ToolStatus
    tool: str
    data: dict[str, Any] = Field(default_factory=dict)
    error: ToolError | None = None

    def to_json_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="json")


def success(tool: str, data: dict[str, Any]) -> dict[str, Any]:
    return ToolEnvelope(status=ToolStatus.SUCCESS, tool=tool, data=data).to_json_dict()


def error(tool: str, code: str, message: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
    return ToolEnvelope(
        status=ToolStatus.ERROR,
        tool=tool,
        data=data or {},
        error=ToolError(code=code, message=message),
    ).to_json_dict()


def partial(tool: str, data: dict[str, Any], message: str) -> dict[str, Any]:
    return ToolEnvelope(
        status=ToolStatus.PARTIAL,
        tool=tool,
        data=data,
        error=ToolError(code="partial_result", message=message),
    ).to_json_dict()


class ParsedDealQuery(BaseModel):
    """Normalized shopping intent extracted from a free-text user query."""

    product: str = Field(description="Core product the user wants, e.g. '75 inch TV'")
    category: str | None = Field(default=None, description="Optional category hint")
    brand: str | None = None
    max_price: float | None = Field(default=None, ge=0)
    min_price: float | None = Field(default=None, ge=0)
    currency: str = "CAD"
    must_have: list[str] = Field(default_factory=list)
    nice_to_have: list[str] = Field(default_factory=list)
    retailer_preference: str | None = None
    search_query: str = Field(description="Concise query string for deal search tools")


class DealCandidate(BaseModel):
    """A single deal candidate used for ranking and final recommendations."""

    title: str
    price: float | None = None
    currency: str = "CAD"
    retailer: str | None = None
    url: str | None = None
    lowvyn_id: str | None = None
    lowvyn_score: float | None = Field(default=None, ge=0, le=100)
    deal_verdict: str | None = None
    savings: float | None = None
    notes: str | None = None


class RankedDeal(DealCandidate):
    rank: int = Field(ge=1)
    rationale: str


class DealReport(BaseModel):
    """Final structured recommendation returned to the user-facing agent turn."""

    query: str
    currency: str = "CAD"
    best_deal: RankedDeal | None = None
    alternatives: list[RankedDeal] = Field(default_factory=list)
    summary: str
    caveats: list[str] = Field(default_factory=list)
    sources_used: list[str] = Field(default_factory=list)
    response_format: Literal["deal_report_v1"] = "deal_report_v1"
