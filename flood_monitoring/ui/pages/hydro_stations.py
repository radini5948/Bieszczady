# -*- coding: utf-8 -*-
# @title Stacje Pomiarowe

import streamlit as st

from flood_monitoring.ui.components.charts import (
    create_comparison_chart,
    create_flow_comparison_chart,
    display_station_charts,
)
from flood_monitoring.ui.components.map import display_map
from datetime import datetime, timedelta
from flood_monitoring.ui.services.api_service import get_station_data, get_stations


# =======================
# Funkcje pomocnicze
# =======================

def get_wojewodztwo(props: dict) -> str:
    """Zwraca województwo, obsługuje oba warianty klucza (z literówką i bez)."""
    return props.get("wojewodztwo", props.get("wojewodztwo:", ""))


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


def get_wojewodztwo_emoji(wojewodztwo: str) -> str:
    """Zwraca emoji dla danego województwa."""
    emoji_map = {
        "dolnośląskie": "️",
        "kujawsko-pomorskie": "",
        "lubelskie": "",
        "lubuskie": "",
        "łódzkie": "",
        "małopolskie": "",
        "mazowieckie": "",
        "opolskie": "",
        "podkarpackie": "",
        "podlaskie": "",
        "pomorskie": "",
        "śląskie": "️",
        "świętokrzyskie": "",
        "warmińsko-mazurskie": "",
        "wielkopolskie": "",
        "zachodniopomorskie": ""
    }
    return emoji_map.get(wojewodztwo, "")


def get_status_emoji(status: str) -> str:
    """Zwraca emoji dla danego statusu stacji."""
    if status == "Aktywne":
        return "✅"
    elif status == "Nieaktywne":
        return "❌"
    else:
        return "⚠️"

def show_hydro_stations():
    """Wyświetl stronę stacji hydrologicznych"""
    st.title(" Mapa Stacji Pomiarowych")
    st.markdown("""Przeglądaj stacje pomiarowe i analizuj dane hydrologiczne.""")

    if 'stations_cache' not in st.session_state:
        st.session_state.stations_cache = {}
    if 'last_stations_fetch' not in st.session_state:
        st.session_state.last_stations_fetch = None

    st.markdown("""
    <style>
    /* Zmniejsz odstępy między elementami */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    /* Kompaktowe metryki */
    [data-testid="metric-container"] {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        padding: 0.5rem;
        border-radius: 0.375rem;
        margin: 0.25rem 0;
    }
    
    /* Zmniejsz odstępy w kolumnach */
    .stColumns > div {
        padding: 0 0.25rem;
    }
    
    /* Kompaktowe selectboxy */
    .stSelectbox > div > div {
        margin-bottom: 0.5rem;
    }
    
    /* Zmniejsz wysokość divider */
    hr {
        margin: 0.5rem 0;
    }
    
    /* Kompaktowe expandery */
    .streamlit-expanderHeader {
        padding: 0.5rem 1rem;
    }
    
    /* Responsywne style dla mapy */
    .map-container {
        width: 100%;
        height: auto;
        min-height: 400px;
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("️ Opcje analizy")

        st.subheader(" Zakres czasowy")
        days_back = st.selectbox(
            "Dane z ostatnich:",
            options=[1, 3, 7, 14, 30, 90],
            index=0,  # domyślnie 1 dzień dla lepszej wydajności
            format_func=lambda x: f"{x} {'dzień' if x == 1 else 'dni' if x < 5 else 'dni'}",
            help=" Domyślnie 1 dzień dla szybszego ładowania. Wybierz więcej dni jeśli potrzebujesz dłuższej historii."
        )

        st.subheader(" Opcje wyświetlania")
        show_trends = st.checkbox("Pokaż linie trendów", value=True)
        show_statistics = st.checkbox("Pokaż statystyki", value=True)
        show_alerts = st.checkbox("Pokaż strefy ostrzeżeń", value=True)

        map_style = st.selectbox(
            " Styl mapy:",
            options=[
                "OpenStreetMap", 
                "OpenStreetMap.HOT", 
                "OpenTopoMap",
                "Satellite", 
                "Terrain", 
                "CartoDB Positron", 
                "CartoDB Dark"
            ],
            index=0,
            help="Wybierz styl mapy dostosowany do Twoich potrzeb"
        )

        st.subheader(" Opcje wydajności")
        use_progressive_loading = st.checkbox(
            "Progresywne ładowanie danych", 
            value=True,
            help="Ładuj dane w mniejszych partiach dla lepszej wydajności"
        )
        if use_progressive_loading:
            batch_size = st.slider(
                "Rozmiar partii danych:",
                min_value=25,
                max_value=200,
                value=50,
                step=25,
                help="Mniejsze wartości = szybsze ładowanie, większe = więcej danych na raz"
            )
        else:
            batch_size = 100

        analysis_type = st.radio(
            "Typ analizy:",
            options=["Pojedyncze stacje", "Porównanie stacji"],
            index=0
        )

    stations = get_stations()
    if not stations:
        st.error("❌ Nie udało się pobrać danych stacji")
        return

    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(" Stacje", len(stations))
    
    with col2:
        active_stations = len([s for s in stations if s["properties"].get('status') != 'inactive'])
        st.metric("✅ Aktywne", active_stations)
    
    with col3:
        provinces_count = len(set(get_wojewodztwo(s["properties"]) for s in stations if get_wojewodztwo(s["properties"])))
        st.metric(" Województwa", provinces_count - 1)
    
    with col4:
        rivers_count = len(set(get_rzeka(s["properties"]) for s in stations if get_rzeka(s["properties"])))
        st.metric(" Rzeki", rivers_count)

    col1, col2 = st.columns(2)
    
    with col1:
        wojewodztwa = sorted(
            list(
                set(
                    [
                        get_wojewodztwo(s["properties"])
                        for s in stations
                        if get_wojewodztwo(s["properties"])
                    ]
                )
            )
        )

        wojewodztwa_with_emoji = [f"{get_wojewodztwo_emoji(woj)} {woj}" for woj in wojewodztwa]

        selected_woj_display = st.selectbox(
            " Wybierz województwo:", [" Wszystkie"] + wojewodztwa_with_emoji
        )

        if selected_woj_display == " Wszystkie":
            selected_woj = "Wszystkie"
        else:
            selected_woj = selected_woj_display.split(" ", 1)[1]  # Usuń emoji i spację
        
        if selected_woj != "Wszystkie":
            filtered_stations = [
                s for s in stations
                if get_wojewodztwo(s["properties"]) == selected_woj
            ]
        else:
            filtered_stations = stations
    
    with col2:
        status_options = [" Wszystkie", "✅ Aktywne", "❌ Nieaktywne"]
        selected_status_display = st.selectbox(
            " Status stacji:", status_options, index=0
        )

        if selected_status_display == " Wszystkie":
            selected_status = "Wszystkie"
        elif selected_status_display == "✅ Aktywne":
            selected_status = "Aktywne"
        elif selected_status_display == "❌ Nieaktywne":
            selected_status = "Nieaktywne"
        
        if selected_status == "Aktywne":
            filtered_stations = [s for s in filtered_stations if s["properties"].get('status') != 'inactive']
        elif selected_status == "Nieaktywne":
            filtered_stations = [s for s in filtered_stations if s["properties"].get('status') == 'inactive']
    
    if not filtered_stations:
        st.warning("Brak stacji w wybranym województwie.")
        return

    with st.expander(" Zaawansowane filtry", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
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
            
            selected_rzeka = st.selectbox(
                " Wybierz rzekę:", ["Wszystkie"] + rzeki, index=0
            )
            
            if selected_rzeka != "Wszystkie":
                filtered_stations = [
                    s for s in filtered_stations
                    if get_rzeka(s["properties"]) == selected_rzeka
                ]
        
        with col2:
            data_types = st.multiselect(
                " Typ dostępnych danych:",
                options=["Poziom wody", "Przepływ", "Temperatura"],
                default=["Poziom wody", "Przepływ"]
            )
    
    if not filtered_stations:
        st.warning("Brak stacji w wybranym województwie / na wybranej rzece.")
        return

    st.markdown("** Wybierz stacje do analizy**")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_term = st.text_input(
            " Wyszukaj stację:",
            placeholder="Wpisz nazwę stacji, rzeki lub miejscowości...",
            help="Wyszukiwanie uwzględnia nazwę stacji, rzekę i miejscowość"
        )
        
        if search_term:
            filtered_stations = [
                s for s in filtered_stations 
                if search_term.lower() in get_stacja(s["properties"]).lower() or 
                   search_term.lower() in (get_rzeka(s["properties"]) or "").lower()
            ]
    
    with col2:
        quick_select = st.selectbox(
            "⚡ Szybki wybór:",
            options=[
                "Wybierz ręcznie",
                "Top 5 stacji",
                "Stacje z największym przepływem",
                "Stacje z najwyższym poziomem"
            ]
        )

    station_options = []
    for station in filtered_stations:
        name = get_stacja(station["properties"])
        river = get_rzeka(station["properties"]) or "Nieznana rzeka"
        province = get_wojewodztwo(station["properties"]) or ""
        
        display_name = f"{name} ({river})"
        if province:
            display_name += f" [{province}]"
            
        station_options.append(display_name)

    default_selection = []
    if quick_select == "Top 5 stacji":
        default_selection = station_options[:5]
    elif quick_select == "Wybierz ręcznie":
        default_selection = station_options[:3] if len(station_options) >= 3 else station_options
    elif quick_select == "Stacje z największym przepływem":
        stations_with_flow = []
        for i, station in enumerate(filtered_stations):
            przeplyw = station["properties"].get('przeplyw')
            if przeplyw is not None and przeplyw > 0:
                stations_with_flow.append((i, przeplyw))

        stations_with_flow.sort(key=lambda x: x[1], reverse=True)
        top_flow_indices = [idx for idx, _ in stations_with_flow[:5]]
        default_selection = [station_options[i] for i in top_flow_indices]
        
        if not default_selection:
            st.warning("️ Brak stacji z dostępnymi danymi o przepływie w wybranym obszarze.")
    elif quick_select == "Stacje z najwyższym poziomem":
        stations_with_level = []
        for i, station in enumerate(filtered_stations):
            stan_wody = station["properties"].get('stan_wody')
            if stan_wody is not None:
                stations_with_level.append((i, stan_wody))

        stations_with_level.sort(key=lambda x: x[1], reverse=True)
        top_level_indices = [idx for idx, _ in stations_with_level[:5]]
        default_selection = [station_options[i] for i in top_level_indices]
        
        if not default_selection:
            st.warning("️ Brak stacji z dostępnymi danymi o poziomie wody w wybranym obszarze.")
    
    max_selections = 10 if analysis_type == "Porównanie stacji" else 5
    
    selected_station_names = st.multiselect(
        f"Wybierz stacje (max {max_selections}):",
        options=station_options,
        default=default_selection,
        help=f"Możesz wybrać do {max_selections} stacji {'do porównania' if analysis_type == 'Porównanie stacji' else 'do analizy'}",
        max_selections=max_selections
    )
    
    if not selected_station_names:
        st.info("️ Wybierz co najmniej jedną stację, aby wyświetlić mapę i dane.")
        return

    selected_stations = []
    for i, station in enumerate(filtered_stations):
        if station_options[i] in selected_station_names:
            selected_stations.append(station)

    st.success(f"✅ Wybrano {len(selected_stations)} {'stację' if len(selected_stations) == 1 else 'stacje' if len(selected_stations) < 5 else 'stacji'}")

    st.markdown("** Mapa wybranych stacji**")

    auto_fit = True
    cluster_markers = False
    responsive_map = True
    
    if selected_stations:
        enhanced_stations_data = []
        for station in selected_stations:
            lat = station["geometry"]["coordinates"][1]
            lon = station["geometry"]["coordinates"][0]
            props = station["properties"]

            stan_wody_display = "Brak danych"
            if props.get('stan_wody') is not None:
                stan_wody_display = f"{props['stan_wody']:.1f} cm"
            
            przeplyw_display = "Brak danych"
            if props.get('przeplyw') is not None:
                przeplyw_display = f"{props['przeplyw']:.2f} m³/s"

            ostatnia_aktualizacja = "Brak danych"
            if props.get('stan_wody_data_pomiaru'):
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(props['stan_wody_data_pomiaru'].replace('Z', '+00:00'))
                    ostatnia_aktualizacja = dt.strftime("%Y-%m-%d %H:%M")
                except:
                    ostatnia_aktualizacja = props.get('stan_wody_data_pomiaru', 'Brak danych')
            elif props.get('przeplyw_data'):
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(props['przeplyw_data'].replace('Z', '+00:00'))
                    ostatnia_aktualizacja = dt.strftime("%Y-%m-%d %H:%M")
                except:
                    ostatnia_aktualizacja = props.get('przeplyw_data', 'Brak danych')
            
            station_data = {
                'lat': lat,
                'lon': lon,
                'name': get_stacja(props),
                'river': get_rzeka(props) or "Nieznana rzeka",
                'code': props.get('id_stacji', 'N/A'),
                'wojewodztwo': get_wojewodztwo(props) or "Nieznane województwo",
                'status': props.get('status', 'active'),
                'ostatnia_aktualizacja': ostatnia_aktualizacja,
                'stan_wody': stan_wody_display,
                'przeplyw': przeplyw_display
            }
            enhanced_stations_data.append(station_data)
        


        display_map(
            stations_data=enhanced_stations_data,
            map_style=map_style,
            cluster_markers=cluster_markers,
            responsive=responsive_map
        )

        if auto_fit and len(selected_stations) > 1:
            st.info(" Mapa została automatycznie dopasowana do wybranych stacji")

        with st.expander(" Szczegóły wybranych stacji", expanded=False):
            station_data = []
            for station in selected_stations:
                props = station["properties"]
                coords = station["geometry"]["coordinates"]
                station_data.append({
                    "Stacja": get_stacja(props),
                    "Rzeka": get_rzeka(props) or "Nieznana",
                    "Województwo": get_wojewodztwo(props) or "Nieznane",
                    "Współrzędne": f"{coords[1]:.4f}, {coords[0]:.4f}",
                    "ID": props.get('id_stacji', 'N/A')
                })
            
            st.dataframe(station_data, use_container_width=True)
    else:
        st.warning("️ Nie znaleziono wybranych stacji na mapie.")

    st.markdown("** Analiza danych hydrologicznych**")
    
    if analysis_type == "Pojedyncze stacje":
        for i, station in enumerate(selected_stations):
            station_id = station["properties"]["id_stacji"]
            station_name = get_stacja(station["properties"])
            
            if station_id:
                with st.expander(f" {station_name} - {get_rzeka(station['properties']) or 'Nieznana rzeka'}", expanded=i==0):
                    cache_key = f"{station_id}_{days_back}_{show_statistics}_{batch_size}"
                    
                    if cache_key in st.session_state.stations_cache:
                        data = st.session_state.stations_cache[cache_key]
                    else:
                        with st.spinner(f"Pobieranie danych dla {station_name}..."):
                            if use_progressive_loading:
                                from flood_monitoring.ui.services.api_service import get_station_data
                                data = get_station_data(station_id, days=days_back, extended=True, limit=batch_size)
                            else:
                                data = get_station_data(station_id, days=days_back, extended=show_statistics, limit=batch_size)
                            if data:
                                st.session_state.stations_cache[cache_key] = data
                    
                    if data:
                        display_station_charts(data)
                    else:
                        st.error(f"❌ Nie udało się pobrać danych dla stacji {station_name}")
            else:
                st.error(f"❌ Brak ID dla stacji {station_name}")
    
    elif analysis_type == "Porównanie stacji" and len(selected_stations) > 1:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            chart_type = st.radio(
                " Wybierz typ wykresu:",
                ["Poziom wody", "Przepływ", "Oba typy"],
                horizontal=True
            )
        
        with col2:
            show_individual = st.checkbox(
                "Pokaż wykresy indywidualne",
                value=False,
                help="Dodatkowo wyświetl wykresy dla każdej stacji osobno"
            )
        
        stations_data = {}

        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, station in enumerate(selected_stations):
            station_id = station["properties"]["id_stacji"]
            station_name = get_stacja(station["properties"])
            
            status_text.text(f"Pobieranie danych: {station_name}...")
            progress_bar.progress((i + 1) / len(selected_stations))
            
            if station_id:
                cache_key = f"{station_id}_{days_back}_{show_statistics}_{batch_size}"
                
                if cache_key in st.session_state.stations_cache:
                    data = st.session_state.stations_cache[cache_key]
                else:
                    if use_progressive_loading:
                        from flood_monitoring.ui.services.api_service import get_station_data
                        data = get_station_data(station_id, days=days_back, extended=True, limit=batch_size)
                    else:
                        data = get_station_data(station_id, days=days_back, extended=show_statistics, limit=batch_size)
                    if data:
                        st.session_state.stations_cache[cache_key] = data
                
                if data:
                    stations_data[station_name] = data
        
        progress_bar.empty()
        status_text.empty()
        
        if stations_data:
            if chart_type in ["Poziom wody", "Oba typy"]:
                comparison_fig = create_comparison_chart(stations_data)
                if comparison_fig:
                    st.plotly_chart(comparison_fig, use_container_width=True)
                else:
                    st.info("️ Brak danych o poziomie wody dla wybranych stacji")
            
            if chart_type in ["Przepływ", "Oba typy"]:
                flow_comparison_fig = create_flow_comparison_chart(stations_data)
                if flow_comparison_fig:
                    st.plotly_chart(flow_comparison_fig, use_container_width=True)
                else:
                    st.info("️ Brak danych o przepływie dla wybranych stacji")

            if show_individual:
                st.subheader(" Wykresy indywidualne")
                for station_name, data in stations_data.items():
                    with st.expander(f" {station_name}", expanded=False):
                        display_station_charts(data)
        else:
            st.error("❌ Nie udało się pobrać danych dla żadnej z wybranych stacji")
    
    elif analysis_type == "Porównanie stacji" and len(selected_stations) <= 1:
        st.info("️ Wybierz co najmniej 2 stacje, aby przeprowadzić porównanie.")


if __name__ == "__main__":
    show_hydro_stations()
