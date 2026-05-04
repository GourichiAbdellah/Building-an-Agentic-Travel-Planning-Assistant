
from mcp.server.fastapi import MCPServer
import random

server = MCPServer("weather-tools")

WEATHER_DB = {
    "barcelona": {"avg_temp_c": 22, "condition": "Ensoleillé", "rain_prob": 10},
    "paris":     {"avg_temp_c": 16, "condition": "Nuageux",    "rain_prob": 35},
    "tokyo":     {"avg_temp_c": 20, "condition": "Partiellement nuageux", "rain_prob": 25},
    "marrakech": {"avg_temp_c": 28, "condition": "Très ensoleillé", "rain_prob": 5},
    "new york":  {"avg_temp_c": 18, "condition": "Variable",   "rain_prob": 20},
}

@server.tool()
def get_weather(destination: str, travel_month: str = "juin") -> dict:
    """
    Returns typical weather for the destination during the given month.
    """
    key = destination.lower()
    data = WEATHER_DB.get(key, {
        "avg_temp_c": 20,
        "condition": "Données non disponibles",
        "rain_prob": 20
    })
    return {
        "destination": destination,
        "month": travel_month,
        **data,
        "recommendation": (
            "Activités en plein air recommandées."
            if data["rain_prob"] < 30
            else "Prévoyez des activités en intérieur en alternance."
        )
    }

server.run(port=3334)
