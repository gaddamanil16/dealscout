# Lowvyn tool selection

Lowvyn MCP URL: `https://api.lowvyn.com/mcp` (streamable HTTP, no API key).

| Tool | When to use |
|------|-------------|
| `intent_search` | Best first call for natural-language needs ("quiet 75 inch TV under 1200") |
| `search_products` | Catalogue exploration with keyword / category / max price / retailer filters |
| `get_product` | Lookup by Lowvyn id or retailer URL for score + verdict |
| `verify_deal` | Confirm whether a price is a real deal vs history |
| `find_cheaper` | Same product cheaper at another Canadian retailer (UPC match) |
| `get_price_history` | Show trend / all-time low context |
| `get_retailers` | List tracked retailers and freshness |
| `get_categories` | Discover category slugs when filtering search |

## Coverage note

Current sources: Amazon.ca, Walmart.ca, BestBuy.ca, Canadian Tire, Canada Computers,
Newegg.ca, Visions.ca. Forum scrapers are planned later and are not available yet.
