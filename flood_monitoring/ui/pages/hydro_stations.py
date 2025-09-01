# -*- coding: utf-8 -*-
# @title Stacje Pomiarowe

import streamlit as st

from flood_monitoring.ui.components.charts import display_station_charts,create_comparison_chart,create_flow_comparison_chart
from flood_monitoring.ui.components.map import create_stations_map, display_map
from flood_monitoring.ui.services.api_service import get_station_data, get_stations


# =======================
# Funkcje pomocnicze
# =======================

def get_wojewodztwo(props: dict) -> str:
    """Zwraca województwo, obsługuje oba warianty klucza (z literówką i bez)."""
    return props.get("wojewodztwo") or props.get("wojewodztwo:")


def get_rzeka(props: dict) -> str:
    """Zwraca nazwę rzeki (jeśli jest)."""
    return props.get("rzeka")


def get_stacja(props: dict) -> str:
    """Zwraca nazwę stacji (jeśli jest)."""
    return props.get("stacja")


def get_bounds(stations):
    """Zwraca bounding box [ [min_lat, min_lon], [max_lat, max_lon] ] dla listy stacji."""
    lats = []
    lons = []
    for s in stations:
        coords = s["geometry"]["coordinates"]  # [lon, lat]
        lons.append(float(coords[0]))
        lats.append(float(coords[1]))
    return [[min(lats), min(lons)], [max(lats), max(lons)]]

# st.set_page_config(page_title="HydroApp", layout="wide")
#
# st.title("🌊 Wizualizacja danych hydrologicznych")

# =======================
# Pobranie danych stacji
# =======================
stations = get_stations()

if not stations:
    st.warning("Nie udało się pobrać danych o stacjach.")
    st.stop()

# =======================
# Filtrowanie wg województwa
# =======================
wojewodztwa = sorted(
    list(
        set(
            [
                get_wojewodztwo(s["properties"])
                for s in stations["features"]
                if get_wojewodztwo(s["properties"])
            ]
        )
    )
)

selected_woj = st.sidebar.selectbox("Wybierz województwo:", ["Wszystkie"] + wojewodztwa)

if selected_woj != "Wszystkie":
    filtered_stations = [
        s for s in stations["features"]
        if get_wojewodztwo(s["properties"]) == selected_woj
    ]
else:
    filtered_stations = stations["features"]

if not filtered_stations:
    st.warning("Brak stacji w wybranym województwie.")
    st.stop()

# =======================
# Filtrowanie wg rzeki
# =======================
rzeki = sorted(
    list(
        set(
            [
                get_rzeka(s["properties"])
                for s in filtered_stations
                if get_rzeka(s["properties"])
            ]
        )
    )
)

selected_rzeka = st.sidebar.selectbox("Wybierz rzekę:", ["Wszystkie"] + rzeki)

if selected_rzeka != "Wszystkie":
    filtered_stations = [
        s for s in filtered_stations
        if get_rzeka(s["properties"]) == selected_rzeka
    ]

if not filtered_stations:
    st.warning("Brak stacji w wybranym województwie / na wybranej rzece.")
    st.stop()

# =======================
# Autocomplete + multiselect razem
# =======================
station_names_all = [get_stacja(s["properties"]) for s in filtered_stations]

# Autocomplete (pojedynczy wybór)
selected_station_autocomplete = st.selectbox(
    "🔎 Wyszukaj stację:",
    options=[""] + sorted(station_names_all),
    index=0,
    help="Zacznij pisać nazwę stacji – lista się zawęzi."
)

# Multiselect (wiele stacji)
selected_stations_multi = st.multiselect("📍 Wybierz stacje do analizy:", station_names_all)

# Połączenie obu źródeł wyboru
selected_stations = set(selected_stations_multi)
if selected_station_autocomplete:
    selected_stations.add(selected_station_autocomplete)

selected_stations = list(selected_stations)

if not selected_stations:
    st.info("Wybierz stację, aby zobaczyć dane.")
    st.stop()

# =======================
# Mapa stacji
# =======================
stations_to_display = [
    s for s in filtered_stations if get_stacja(s["properties"]) in selected_stations
]

m = create_stations_map({"type": "FeatureCollection", "features": stations_to_display})

if selected_woj != "Wszystkie" and stations_to_display:
    bounds = get_bounds(stations_to_display)
    m.fit_bounds(bounds)

display_map(m)

# =======================
# Pobranie i wyświetlenie danych
# =======================
stations_data = {}
for st_name in selected_stations:
    station = next(s for s in filtered_stations if get_stacja(s["properties"]) == st_name)
    station_id = station["properties"]["id_stacji"]
    data = get_station_data(station_id)
    if data:
        stations_data[st_name] = data

if stations_data:
    if len(stations_data) == 1:
        display_station_charts(next(iter(stations_data.values())))
    else:
        st.subheader("📊 Porównanie wybranych stacji")
        st.plotly_chart(create_comparison_chart(stations_data), use_container_width=True)
        st.plotly_chart(create_flow_comparison_chart(stations_data), use_container_width=True)
