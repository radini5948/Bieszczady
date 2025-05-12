"""
Serwis do komunikacji z API
"""
import os
from typing import Any, Dict, List

import requests

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


def get_stations() -> List[Dict[str, Any]]:
    """Pobierz listę stacji pomiarowych"""
    try:
        response = requests.get(f"{BACKEND_URL}/stations")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise Exception(f"Error fetching stations: {str(e)}")


def get_station_data(station_id: str, days: int = 7) -> List[Dict[str, Any]]:
    """Pobierz dane z konkretnej stacji"""
    try:
        response = requests.get(
            f"{BACKEND_URL}/stations/{station_id}", params={"days": days}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise Exception(f"Error fetching station data: {str(e)}")
