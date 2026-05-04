
from mcp.server.fastapi import MCPServer

server = MCPServer("budget-tools")

@server.tool()
def estimate_budget(destination: str, days: int) -> dict:
    """
    Estimate total travel budget in USD.
    Returns breakdown: accommodation, food, transport, activities.
    """
    costs = {
        "accommodation": 80 * days,
        "food":          40 * days,
        "transport":     30 * days,
        "activities":    20 * days,
    }
    costs["total"] = sum(costs.values())
    costs["destination"] = destination
    costs["days"] = days
    return costs

server.run(port=3333)
