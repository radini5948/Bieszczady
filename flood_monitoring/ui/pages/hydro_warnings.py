import streamlit as st
import folium
from streamlit_folium import folium_static
import requests
from typing import List, Dict
from flood_monitoring.ui.services.api_service import get_warnings

# Funkcje pomocnicze
def aggregate_warnings_by_woj(warnings: List[Dict]) -> Dict[str, List[Dict]]:
    """Agreguj ostrzeżenia po województwach"""
    woj_warnings = {}
    for warning in warnings:
        for area in warning.get("obszary", []):
            woj = area.get("wojewodztwo")
            if woj:
                if woj not in woj_warnings:
                    woj_warnings[woj] = []
                woj_warnings[woj].append(warning)
    return woj_warnings

def get_color(max_stopien: str) -> str:
    """Zwraca kolor na podstawie najwyższego stopnia ostrzeżenia"""
    stopien_num = int(max_stopien) if max_stopien.isdigit() else 0
    if stopien_num == 3:
        return "#ff0000"
    elif stopien_num == 2:
        return "#ffa500"
    elif stopien_num == 1:
        return "#ffff00"
    else:
        return "#ffffff"

def popup_html_for_woj(woj_name: str, woj_warnings: Dict[str, List[Dict]]) -> str:
    """Tworzy HTML do popupa dla województwa"""
    if woj_name not in woj_warnings:
        return "Brak ostrzeżeń"
    html = f"<b>Ostrzeżenia dla {woj_name}:</b><br><ul>"
    for warning in woj_warnings[woj_name]:
        html += f"<li><b>{warning['zdarzenie']}</b> (stopień {warning['stopien']})<br>"
        html += f"Od: {warning['data_od']} Do: {warning['data_do']}<br>"
        html += f"Komentarz: {warning.get('komentarz', '-')}</li><br>"
    html += "</ul>"
    return html

# --- Główna strona ---
st.title("Mapa Ostrzeżeń Hydrologicznych")

warnings = get_warnings()
if not warnings:
    st.warning("Brak ostrzeżeń do wyświetlenia.")
    st.stop()

# Grupowanie ostrzeżeń po województwach
woj_warnings_all = aggregate_warnings_by_woj(warnings)

# Multi-select do filtrowania województw
wojewodztwa_options = sorted(list(woj_warnings_all.keys()))
selected_wojewodztwa = st.multiselect(
    "Wybierz województwa do wyświetlenia:",
    options=wojewodztwa_options,
    default=wojewodztwa_options  # domyślnie wszystkie
)

# Filtrowanie ostrzeżeń
woj_warnings = {woj: woj_warnings_all[woj] for woj in selected_wojewodztwa}

# Pobranie GeoJSON województw (raw link)
geojson_url = "https://raw.githubusercontent.com/ppatrzyk/polska-geojson/master/wojewodztwa/wojewodztwa-max.geojson"
geojson_data = requests.get(geojson_url).json()

# Tworzenie mapy
m = folium.Map(location=[52.0, 19.0], zoom_start=6)

def style_function(feature):
    woj_name = feature['properties']['nazwa']
    max_stopien = "0"
    if woj_name in woj_warnings:
        max_stopien = max([w['stopien'] for w in woj_warnings[woj_name]], key=int)
    return {
        'fillColor': get_color(max_stopien),
        'color': 'black',
        'weight': 1,
        'fillOpacity': 0.6,
    }

# Dodanie województw z popupami
for feature in geojson_data['features']:
    woj_name = feature['properties']['nazwa']
    popup = folium.Popup(popup_html_for_woj(woj_name, woj_warnings), max_width=350)
    folium.GeoJson(
        feature,
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(fields=['nazwa'], aliases=['Województwo:']),
        popup=popup
    ).add_to(m)

# Wyświetlenie mapy
folium_static(m, width=1200, height=600)

# Lista ostrzeżeń pod mapą, filtrowana
st.subheader("Lista Ostrzeżeń")
for woj in selected_wojewodztwa:
    for warning in woj_warnings[woj]:
        with st.expander(f"Ostrzeżenie {warning['numer']} - {warning['stopien']} ({woj})"):
            st.write(f"Opublikowano: {warning['opublikowano']}")
            st.write(f"Od: {warning['data_od']} Do: {warning['data_do']}")
            st.write(f"Prawdopodobieństwo: {warning['prawdopodobienstwo']}")
            st.write(f"Zdarzenie: {warning['zdarzenie']}")
            st.write(f"Przebieg: {warning['przebieg']}")
            st.write(f"Komentarz: {warning['komentarz']}")
            st.write("Obszary:")
            for area in warning["obszary"]:
                st.write(f"- {area['wojewodztwo']}: {area['opis']}")
