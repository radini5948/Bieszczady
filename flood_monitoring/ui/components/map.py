"""
Komponent mapy z lokalizacjami stacji
"""
from typing import Any, Dict

import folium
import streamlit as st
from streamlit_folium import folium_static


def create_stations_map(geojson_data: Dict[str, Any]) -> folium.Map:
    """Utwórz mapę z lokalizacjami stacji w formacie GeoJSON"""
    m = folium.Map(location=[52.0, 19.0], zoom_start=6)

    try:
        folium.GeoJson(
            geojson_data,
            name="stations",
            popup=folium.GeoJsonPopup(
                fields=["nazwa_stacji", "rzeka"],
                aliases=["Nazwa stacji", "Rzeka"],
                localize=True,
            ),
            tooltip=folium.GeoJsonTooltip(
                fields=["nazwa_stacji"],
                aliases=[""],
                style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
            ),
            marker=folium.CircleMarker(
                radius=8,
                weight=2,
                color="blue",
                fill_color="blue",
                fill_opacity=0.6
            ),
        ).add_to(m)
    except Exception as e:
        st.error(f"Error adding stations to map: {str(e)}")
        st.write("Problematic GeoJSON data:", geojson_data)

    return m


def display_map(m: folium.Map, width: int = 1200, height: int = 600):
    """Wyświetl mapę w aplikacji Streamlit"""
    folium_static(m, width=width, height=height)
