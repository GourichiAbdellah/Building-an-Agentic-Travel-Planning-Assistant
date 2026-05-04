
from mcp.server.fastapi import MCPServer

server = MCPServer("travel-search-tools")

DESTINATIONS = {
    "barcelona": {
        "country": "Espagne",
        "language": "Catalan / Espagnol",
        "attractions": [
            "Sagrada Família", "Parc Güell", "Las Ramblas",
            "Musée Picasso", "Camp Nou", "Barri Gòtic"
        ],
        "activities": [
            "Visite architecturale Gaudí", "Plages de Barceloneta",
            "Dégustation tapas", "Marché de la Boqueria"
        ],
        "visa_required": False,
        "best_season": "Avril – Octobre"
    },
    "paris": {
        "country": "France",
        "language": "Français",
        "attractions": [
            "Tour Eiffel", "Musée du Louvre", "Notre-Dame",
            "Arc de Triomphe", "Montmartre"
        ],
        "activities": [
            "Croisière sur la Seine", "Visite des musées",
            "Shopping Champs-Élysées", "Excursion Versailles"
        ],
        "visa_required": False,
        "best_season": "Avril – Juin, Septembre – Octobre"
    },
    "marrakech": {
        "country": "Maroc",
        "language": "Arabe / Français",
        "attractions": [
            "Place Jemaa el-Fna", "Médina", "Palais Bahia",
            "Jardins Majorelle", "Souks"
        ],
        "activities": [
            "Visite des souks", "Excursion Atlas", "Hammam traditionnel",
            "Cours de cuisine marocaine"
        ],
        "visa_required": False,
        "best_season": "Mars – Mai, Septembre – Novembre"
    },
}

@server.tool()
def search_destination(destination: str) -> dict:
    """
    Returns tourist info, attractions, and activities for a destination.
    """
    key = destination.lower()
    if key in DESTINATIONS:
        return DESTINATIONS[key]
    return {
        "info": f"Destination '{destination}' non trouvée dans la base locale.",
        "suggestion": "Destinations disponibles : " + ", ".join(DESTINATIONS.keys())
    }

server.run(port=3337)
