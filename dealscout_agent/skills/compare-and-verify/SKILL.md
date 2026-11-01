---
name: compare-and-verify
description: >
  Use when the user wants to verify whether a listed price is a real deal, or
  compare the same product across retailers after candidates are found.
---

# Compare and Verify

## Goal

Validate that a recommended price is genuine and check whether another Canadian
retailer has the same item cheaper.

## Workflow

1. Identify a product by Lowvyn id, retailer URL, or `canonicalUrl` from search.
2. Call `verify_deal` with `idOrUrl` and optional `claimedPrice`.
3. If verdict is `real_deal` or `modest_deal`, optionally call `find_cheaper`.
4. If history context helps the user decide, call `get_price_history`.
5. Fold verification outcomes into candidate `notes` / `deal_verdict` before
   calling `rank_deal_candidates`.

## Decision guide

| Verdict | Meaning | Action |
|---------|---------|--------|
| `real_deal` | Strong vs history | Prefer in ranking |
| `modest_deal` | Mild savings | Keep as alternative |
| `average` | Not special | Downgrade unless unique features |
| `bad_time` | Poor vs history | Avoid as "best deal" |
| `insufficient_data` | Not enough history | Disclose uncertainty |

## Resources

- Read `references/verification-checklist.md` before finalizing a recommendation.
