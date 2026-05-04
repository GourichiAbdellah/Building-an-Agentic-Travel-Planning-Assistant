
from mcp.server.fastapi import MCPServer

server = MCPServer("calculator-tools")

@server.tool()
def calculate(expression: str) -> dict:
    """
    Evaluates a safe arithmetic expression (ex: '(120 * 5) + 30').
    Supports: +, -, *, /, **, (, )
    """
    import re
    # Sécurité : autorise seulement les caractères arithmétiques
    if not re.match(r"^[\d\s\+\-\*\/\.\(\)\*\*]+$", expression):
        return {"error": "Expression non autorisée.", "expression": expression}
    try:
        result = eval(expression)
        return {"expression": expression, "result": round(result, 4)}
    except Exception as e:
        return {"error": str(e), "expression": expression}

server.run(port=3336)
