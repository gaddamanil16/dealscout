# Structured response rules

## Local tool envelopes

All local tools return:

```json
{
  "status": "success | error | partial",
  "tool": "tool_name",
  "data": {},
  "error": null
}
```

Always consume `data` on success. On `error` / `partial`, read `error.message`.

## Final report

`build_deal_report` emits `data.report` matching `assets/deal-response.schema.json`
(`response_format = deal_report_v1`).

User-facing answer should mirror:

1. **Best deal** — title, price, retailer, verdict/score, link
2. **Why it wins** — from summary / rationale
3. **Alternatives** — up to 3
4. **Caveats** — currency, coverage limits, missing history, etc.
