"""
Strona z monitorowaniem stacji pomiarowych
"""
# -*- coding: utf-8 -*-
# @title Stacje Pomiarowe

import streamlit as st

from flood_monitoring.ui.components.charts import display_station_charts
from flood_monitoring.ui.components.map import create_stations_map, display_map
from flood_monitoring.ui.services.api_service import get_station_data, get_stations

# Ustawienie nazwy strony w menu
st.sidebar.markdown("# Stacje Pomiarowe")

st.title("Stacje pomiarowe")

# Main layout
try:
    # Get stations data
    stations = get_stations()

    if not stations:
        st.warning("Nie udało się pobrać danych o stacjach.")
        st.stop()

    # Create and display map
    m = create_stations_map(stations)
    display_map(m)

    # Station selection
    station_names = [station["properties"]["nazwa_stacji"] for station in stations["features"]]
    selected_station = st.selectbox("Wybierz stację:", station_names)

    if selected_station:
        station = next(s for s in stations["features"] if s["properties"]["nazwa_stacji"] == selected_station)
        st.subheader(f"Stacja: {station['properties']['nazwa_stacji']}")

        # Get and display station data
        data = get_station_data(station["properties"]["id_stacji"])
        if data:
            # Debug information
            st.write("Debug - Station ID:", station["properties"]["id_stacji"])
            st.write("Debug - Raw data:", data)
            display_station_charts(data)

except Exception as e:
    st.error(f"Wystąpił błąd: {str(e)}")
    st.info("Upewnij się, że backend jest uruchomiony i dostępny.")
