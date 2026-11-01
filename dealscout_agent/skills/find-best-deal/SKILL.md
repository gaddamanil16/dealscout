---
name: find-best-deal
description: >
  Use when the user asks to find, discover, or recommend the best shopping deal
  for a product (TVs, laptops, appliances, etc.). Loads the deal-finding
  workflow, Lowvyn tool usage order, and the structured JSON response schema.
---

# Find Best Deal

## Goal

Turn a free-text shopping request into a verified best-deal recommendation with
structured JSON tool results.

## Workflow

1. Call `parse_deal_query` with the raw user text.
   - Read `data.search_query`, `data.max_price`, `data.brand`, and `data.must_have`.
2. Search Lowvyn (prefer in this order):
   - `intent_search` with a plain-language need derived from the parsed query.
   - If results are thin, fall back to `search_products` with `search_query`
     and optional `max_price` / retailer filters.
3. For the top 3–5 promising products:
   - `get_product` for score / verdict details when needed.
   - `verify_deal` to confirm the live price is a genuine deal.
   - Optionally `find_cheaper` to check other Canadian retailers.
4. Pass candidate objects into `rank_deal_candidates` as a JSON array string.
5. Call `build_deal_report` with the ranked list and a short summary.
6. Answer the user using `data.report` from `build_deal_report`.

## Hard constraints

- Never fabricate Lowvyn scores, verdicts, prices, or URLs.
- Prefer `real_deal` / higher Lowvyn Score over merely lowest sticker price.
- State that coverage is Canadian retailers via Lowvyn (CAD).
- If nothing qualifies, return an honest "no strong deal found" summary with
  the closest alternatives and caveats.

## Resources

- Read `references/lowvyn-tools.md` for tool selection guidance.
- Read `references/response-schema.md` before composing the final answer.
- Use `assets/deal-response.schema.json` as the canonical report shape.
