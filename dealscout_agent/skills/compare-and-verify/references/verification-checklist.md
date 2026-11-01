# Verification checklist

Before calling a deal the "best":

- [ ] Product title matches the user's intent (size, brand, key features).
- [ ] `verify_deal` has been called on the leading candidate (when an id/URL exists).
- [ ] Cross-retailer check via `find_cheaper` was considered.
- [ ] Currency is stated as CAD for Lowvyn results.
- [ ] Caveats mention missing history, limited coverage, or stock uncertainty.
- [ ] Final payload went through `build_deal_report` so the tool return is structured JSON.
