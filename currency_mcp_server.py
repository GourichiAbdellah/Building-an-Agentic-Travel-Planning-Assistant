
from mcp.server.fastapi import MCPServer

server = MCPServer("currency-tools")

EXCHANGE_RATES = {
    "USD": 1.0,
    "EUR": 0.92,
    "MAD": 10.05,
    "GBP": 0.79,
    "JPY": 157.0,
    "CAD": 1.36,
    "AED": 3.67,
}

@server.tool()
def convert_currency(amount_usd: float, target_currency: str) -> dict:
    """
    Converts an amount in USD to the target currency.
    """
    currency = target_currency.upper()
    rate = EXCHANGE_RATES.get(currency)
    if rate is None:
        return {"error": f"Devise '{currency}' non supportée.",
                "supported": list(EXCHANGE_RATES.keys())}
    return {
        "amount_usd": amount_usd,
        "target_currency": currency,
        "exchange_rate": rate,
        "converted_amount": round(amount_usd * rate, 2)
    }

server.run(port=3335)
