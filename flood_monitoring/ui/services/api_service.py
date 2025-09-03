"""Serwis do komunikacji z API"""
import os
from typing import Any, Dict, List

import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


@st.cache_data(ttl=300)  # Cache na 5 minut
def get_stations() -> List[Dict[str, Any]]:
    """Pobierz listę stacji pomiarowych"""
    try:
        response = requests.get(f"{BACKEND_URL}/stations/")
        response.raise_for_status()
        data = response.json()
        # Zwróć listę features z GeoJSON
        return data.get('features', [])
    except Exception as e:
        raise Exception(f"Error fetching stations: {str(e)}")


@st.cache_data(ttl=120)  # Cache na 2 minuty dla danych pomiarowych
def get_station_data(station_id: str, days: int = 1, extended: bool = True, limit: int = 100) -> List[Dict[str, Any]]:
    """Pobierz dane z konkretnej stacji"""
    try:
        params = {
            "days": days,
            "extended": extended,
            "limit": limit
        }
        response = requests.get(
            f"{BACKEND_URL}/stations/{station_id}/", params=params
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise Exception(f"Error fetching station data: {str(e)}")

# Funkcja get_station_data_batch została usunięta - używaj get_station_data z parametrem limit

@st.cache_data(ttl=180)  # Cache na 3 minuty dla ostrzeżeń
def get_warnings() -> List[Dict]:
    """Pobierz ostrzeżenia z backendu"""
    try:
        #backend_url = "http://localhost:8000"  # Align with api_service.py
        response = requests.get(f"{BACKEND_URL}/warnings/")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise Exception(f"Error fetching stations: {str(e)}")
        # return []
