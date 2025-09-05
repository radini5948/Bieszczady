import streamlit as st
import folium
from streamlit_folium import folium_static
import requests
import pandas as pd
from datetime import datetime
from typing import List, Dict
from flood_monitoring.ui.services.api_service import get_warnings

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
    if max_stopien == "3":
        return "#ff0000"
    elif max_stopien == "2":
        return "#ffa500"
    elif max_stopien == "1":
        return "#ffff00"
    elif max_stopien == "-1":
        return "#87ceeb"
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
        html += f"Komentarz: {warning.get('przebieg', '-')}</li><br>"
    html += "</ul>"
    return html

def show_hydro_warnings():
    """Wyświetl stronę ostrzeżeń hydrologicznych"""

    st.title("️Mapa Ostrzeżeń Hydrologicznych")
    st.markdown("""Monitoruj aktualne ostrzeżenia hydrologiczne w Polsce z zaawansowanymi narzędziami analizy i filtrowania.""")

    with st.sidebar:
        st.header(" Opcje filtrowania")

        warning_levels = st.multiselect(
            "Poziomy ostrzeżeń:",
            options=["-1", "1", "2", "3"],
            default=["-1", "1", "2", "3"],
            help="Wybierz poziomy ostrzeżeń do wyświetlenia (-1: susza hydrologiczna, 1-3: standardowe ostrzeżenia)"
        )
        
        st.divider()

        st.subheader(" Opcje wyświetlania")
        show_details = st.checkbox("Pokaż szczegóły ostrzeżeń", value=True)
        group_by_province = st.checkbox("Grupuj według województw", value=True)
        show_statistics = st.checkbox("Pokaż statystyki", value=True)
        
        st.divider()

        if st.button(" Odśwież dane ostrzeżeń", help="Wyczyść cache i pobierz najnowsze dane"):
            st.cache_data.clear()
            st.rerun()
        
        st.divider()

        st.subheader(" Widok mapy")
        map_view = st.selectbox(
            "Styl mapy:",
            options=["OpenStreetMap", "Satellite", "Terrain"],
            index=0
        )

    try:
        warnings = get_warnings()
        st.success(f" Pobrano {len(warnings)} ostrzeżeń")

        if warning_levels:
            warnings = [w for w in warnings if str(w.get('stopien', 1)) in warning_levels]

        if show_statistics:
            st.subheader(" Statystyki ostrzeżeń")
            
            total_warnings = len(warnings)
            level_minus1 = len([w for w in warnings if str(w.get('stopien', 1)) == '-1'])
            level_1 = len([w for w in warnings if str(w.get('stopien', 1)) == '1'])
            level_2 = len([w for w in warnings if str(w.get('stopien', 1)) == '2'])
            level_3 = len([w for w in warnings if str(w.get('stopien', 1)) == '3'])
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("Łącznie ostrzeżeń", total_warnings)
            with col2:
                st.metric("🔵 Susza (-1)", level_minus1)
            with col3:
                st.metric("🟡 Poziom 1", level_1)
            with col4:
                st.metric("🟠 Poziom 2", level_2)
            with col5:
                st.metric("🔴 Poziom 3", level_3)
            
            st.divider()

        woj_warnings = aggregate_warnings_by_woj(warnings)

        st.subheader(" Mapa ostrzeżeń hydrologicznych")

        col1, col2 = st.columns([3, 1])
        
        with col2:
            st.markdown("**Legenda mapy:**")
            st.markdown("🔵 Poziom -1 - Susza hydrologiczna")
            st.markdown("🟡 Poziom 1 - Ostrzeżenie")
            st.markdown("🟠 Poziom 2 - Alert")
            st.markdown("🔴 Poziom 3 - Alarm")
            st.markdown("⚪ Brak ostrzeżeń")
        
        with col1:
            m = folium.Map(location=[52.0, 19.0], zoom_start=6)

            if map_view == "Satellite":
                folium.TileLayer(
                    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                    attr='Esri',
                    name='Satellite',
                    overlay=False,
                    control=True
                ).add_to(m)
            elif map_view == "Terrain":
                folium.TileLayer(
                    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Terrain_Base/MapServer/tile/{z}/{y}/{x}',
                    attr='Esri',
                    name='Terrain',
                    overlay=False,
                    control=True
                ).add_to(m)

            wojewodztwa_coords = {
                "dolnośląskie": [51.1, 17.0],
                "kujawsko-pomorskie": [53.0, 18.0],
                "lubelskie": [51.2, 22.9],
                "lubuskie": [52.0, 15.5],
                "łódzkie": [51.8, 19.5],
                "małopolskie": [50.0, 20.0],
                "mazowieckie": [52.2, 21.0],
                "opolskie": [50.7, 17.9],
                "podkarpackie": [49.8, 22.0],
                "podlaskie": [53.1, 23.2],
                "pomorskie": [54.2, 18.2],
                "śląskie": [50.3, 19.0],
                "świętokrzyskie": [50.9, 20.6],
                "warmińsko-mazurskie": [53.8, 20.5],
                "wielkopolskie": [52.4, 17.0],
                "zachodniopomorskie": [53.4, 15.6]
            }

            markers_added = 0
            for woj, coords in wojewodztwa_coords.items():
                if woj in woj_warnings:
                    max_level = max([int(w.get('stopien', 1)) for w in woj_warnings[woj]])
                    color = get_color(str(max_level))
                    
                    folium.CircleMarker(
                        location=coords,
                        radius=15,
                        popup=folium.Popup(popup_html_for_woj(woj, woj_warnings), max_width=400),
                        color='black',
                        weight=2,
                        fillColor=color,
                        fillOpacity=0.7
                    ).add_to(m)
                    markers_added += 1
                else:
                    folium.CircleMarker(
                        location=coords,
                        radius=8,
                        popup=f"<b>{woj.title()}</b><br>Brak ostrzeżeń",
                        color='gray',
                        weight=1,
                        fillColor='white',
                        fillOpacity=0.5
                    ).add_to(m)
            


            folium_static(m, width=700, height=500)

        if show_details and warnings:
            st.subheader(" Szczegóły ostrzeżeń")

            selected_wojewodztwa = st.multiselect(
                "Wybierz województwa do wyświetlenia:",
                options=list(woj_warnings.keys()),
                default=list(woj_warnings.keys())[:5] if len(woj_warnings) > 5 else list(woj_warnings.keys()),
                help="Wybierz województwa, dla których chcesz zobaczyć szczegóły ostrzeżeń"
            )
            
            if selected_wojewodztwa:
                col1, col2 = st.columns(2)
                
                with col1:
                    sort_by = st.selectbox(
                        "Sortuj według:",
                        options=["Województwo", "Poziom ostrzeżenia", "Data wydania", "Numer"],
                        index=0
                    )
                
                with col2:
                    sort_order = st.selectbox(
                        "Kolejność:",
                        options=["Rosnąco", "Malejąco"],
                        index=1
                    )
                
                for woj in selected_wojewodztwa:
                    warnings_list = woj_warnings[woj]

                    if sort_by == "Poziom ostrzeżenia":
                        warnings_list = sorted(warnings_list, key=lambda x: x.get('stopien', 1), reverse=(sort_order == "Malejąco"))
                    elif sort_by == "Numer":
                        warnings_list = sorted(warnings_list, key=lambda x: x.get('numer', ''), reverse=(sort_order == "Malejąco"))
                    
                    with st.expander(f"️ {woj} ({len(warnings_list)} {'ostrzeżenie' if len(warnings_list) == 1 else 'ostrzeżenia' if len(warnings_list) < 5 else 'ostrzeżeń'})", expanded=False):
                        for i, warning in enumerate(warnings_list):
                            level = warning.get('stopien', 1)
                            level_emoji = "🔵" if level =="-1" else "🟡" if level == "1" else "🟠" if level == "2" else  level =="3"
                            
                            col1, col2 = st.columns([1, 3])
                            
                            with col1:
                                st.markdown(f"### {level_emoji}")
                                st.markdown(f"**Poziom {level}**")
                            
                            with col2:
                                st.markdown(f"""
                                ** Numer:** {warning.get('numer', 'Nieznany')}
                                ** Opublikowano:** {warning.get('opublikowano', 'Nieznana')}
                                ** Od:** {warning.get('data_od', 'Nieznana')} **Do:** {warning.get('data_do', 'Nieznana')}
                                ** Zdarzenie:** {warning.get('zdarzenie', 'Nieznane')}
                                ** Prawdopodobieństwo:** {warning.get('prawdopodobienstwo', 'Nieznane')}
                                ** Przebieg:** {warning.get('przebieg', 'Brak opisu')}
                                ** Komentarz:** {warning.get('komentarz', 'Brak komentarza')}
                                """)
                                
                                if warning.get("obszary"):
                                    st.write("** Obszary:**")
                                    for area in warning["obszary"]:
                                        st.write(f"- {area.get('wojewodztwo', 'Nieznane')}: {area.get('opis', 'Brak opisu')}")
                            
                            if i < len(warnings_list) - 1:
                                st.divider()
            else:
                st.info("️ Brak ostrzeżeń do wyświetlenia")
        
    except Exception as e:
        st.error(f" Błąd podczas pobierania ostrzeżeń: {str(e)}")
        st.info(" Sprawdź połączenie z API lub spróbuj ponownie później.")
