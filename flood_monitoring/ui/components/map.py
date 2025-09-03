"""
Komponent mapy z lokalizacjami stacji
"""
from typing import Any, Dict

import folium
import streamlit as st
from streamlit_folium import folium_static, st_folium
import hashlib
import json


def get_wojewodztwo_emoji(wojewodztwo: str) -> str:
    """Zwraca emoji dla danego województwa."""
    emoji_map = {
        "dolnośląskie": "⛰️",
        "kujawsko-pomorskie": "🌾", 
        "lubelskie": "🌻",
        "lubuskie": "🌲",
        "łódzkie": "🏭",
        "małopolskie": "🏔️",
        "mazowieckie": "🏛️",
        "opolskie": "🌿",
        "podkarpackie": "🦌",
        "podlaskie": "🦬",
        "pomorskie": "🌊",
        "śląskie": "⚒️",
        "świętokrzyskie": "⛪",
        "warmińsko-mazurskie": "🦢",
        "wielkopolskie": "🌾",
        "zachodniopomorskie": "🏖️"
    }
    return emoji_map.get(wojewodztwo, "🗺️")


def get_status_emoji_and_text(status: str) -> tuple:
    """Zwraca emoji i tekst dla danego statusu stacji."""
    if status == 'active':
        return "✅", "Aktywna"
    elif status == 'warning':
        return "⚠️", "Ostrzeżenie"
    elif status == 'alarm':
        return "🚨", "Alarm"
    elif status == 'inactive':
        return "❌", "Nieaktywna"
    else:
        return "❓", "Nieznany"


def create_stations_map(stations_data: list, map_style: str = "OpenStreetMap", cluster_markers: bool = False, responsive: bool = True) -> folium.Map:
    """Utwórz mapę z lokalizacjami stacji pomiarowych z ulepszonymi funkcjonalnościami OSM"""
    # Centrum Polski
    center_lat, center_lon = 52.0, 19.0
    
    # Dostępne style map z optymalizowanymi opcjami OSM
    tile_options = {
        "OpenStreetMap": {
            "tiles": "OpenStreetMap",
            "attr": "© OpenStreetMap contributors",
            "max_zoom": 18
        },
        "OpenStreetMap.HOT": {
            "tiles": "https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png",
            "attr": "© OpenStreetMap contributors, Tiles courtesy of Humanitarian OpenStreetMap Team",
            "max_zoom": 17
        },
        "Satellite": {
            "tiles": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            "attr": "Esri",
            "max_zoom": 17
        },
        "Terrain": {
            "tiles": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Terrain_Base/MapServer/tile/{z}/{y}/{x}",
            "attr": "Esri",
            "max_zoom": 13
        },
        "CartoDB Positron": {
            "tiles": "CartoDB positron",
            "attr": "© OpenStreetMap contributors, © CartoDB",
            "max_zoom": 18
        },
        "CartoDB Dark": {
            "tiles": "CartoDB dark_matter",
            "attr": "© OpenStreetMap contributors, © CartoDB",
            "max_zoom": 18
        },
        "OpenTopoMap": {
            "tiles": "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
            "attr": "© OpenStreetMap contributors, © OpenTopoMap",
            "max_zoom": 15
        }
    }
    
    # Utwórz mapę z responsywnymi ustawieniami i lepszą obsługą błędów
    map_kwargs = {
        "location": [center_lat, center_lon],
        "zoom_start": 6,
        "prefer_canvas": True,  # Lepsza wydajność
        "control_scale": True   # Dodaj skalę
    }
    
    # Pobierz konfigurację dla wybranego stylu mapy
    style_config = tile_options.get(map_style, tile_options["OpenStreetMap"])
    
    # Dodaj konfigurację kafelków do argumentów mapy
    map_kwargs.update({
        "tiles": style_config["tiles"],
        "attr": style_config["attr"],
        "max_zoom": style_config["max_zoom"]
    })
    
    # Utwórz mapę z optymalizowaną konfiguracją
    m = folium.Map(**map_kwargs)
    
    # Dodaj dodatkowe warstwy map dla lepszej funkcjonalności OSM
    if map_style == "OpenStreetMap":
        # Dodaj alternatywne warstwy z optymalizowaną konfiguracją
        cartodb_positron = tile_options["CartoDB Positron"]
        folium.TileLayer(
            cartodb_positron["tiles"], 
            name='CartoDB Positron',
            attr=cartodb_positron["attr"],
            max_zoom=cartodb_positron["max_zoom"]
        ).add_to(m)
        
        cartodb_dark = tile_options["CartoDB Dark"]
        folium.TileLayer(
            cartodb_dark["tiles"], 
            name='CartoDB Dark',
            attr=cartodb_dark["attr"],
            max_zoom=cartodb_dark["max_zoom"]
        ).add_to(m)
        
        osm_hot = tile_options["OpenStreetMap.HOT"]
        folium.TileLayer(
            osm_hot["tiles"],
            name='OpenStreetMap HOT',
            attr=osm_hot["attr"],
            max_zoom=osm_hot["max_zoom"]
        ).add_to(m)
        
        topo_map = tile_options["OpenTopoMap"]
        folium.TileLayer(
            topo_map["tiles"],
            name='OpenTopoMap',
            attr=topo_map["attr"],
            max_zoom=topo_map["max_zoom"]
        ).add_to(m)
        
        folium.LayerControl(position='topright').add_to(m)
    
    # Dodaj markery stacji z optymalizacją wydajności
    if stations_data:
        # Ograniczenie liczby markerów dla lepszej wydajności
        max_markers = 500
        limited_stations = stations_data[:max_markers] if len(stations_data) > max_markers else stations_data
        
        if cluster_markers and len(limited_stations) > 50:
            # Użyj klasterowania dla dużej liczby markerów
            try:
                from folium.plugins import MarkerCluster
                marker_cluster = MarkerCluster(
                    name="Stacje hydrologiczne",
                    overlay=True,
                    control=True,
                    icon_create_function="""
                    function(cluster) {
                        return L.divIcon({
                            html: '<div style="background-color: #3498db; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 12px;">' + cluster.getChildCount() + '</div>',
                            className: 'marker-cluster-custom',
                            iconSize: L.point(30, 30)
                        });
                    }
                    """
                ).add_to(m)
                
                # Dodaj markery do klastra
                for station in limited_stations:
                    try:
                        lat = float(station.get('lat', 0))
                        lon = float(station.get('lon', 0))
                        
                        if lat != 0 and lon != 0:
                            # Określ kolor markera na podstawie statusu
                            status = station.get('status', 'unknown')
                            if status == 'alarm':
                                color = 'red'
                                icon = 'exclamation-triangle'
                            elif status == 'warning':
                                color = 'orange'
                                icon = 'exclamation-circle'
                            elif status == 'active':
                                color = 'green'
                                icon = 'tint'
                            else:
                                color = 'gray'
                                icon = 'question'
                            
                            # Utwórz popup z informacjami o stacji
                            popup_html = f"""
                            <div style="width: 280px; font-family: Arial, sans-serif;">
                                <h4 style="margin: 0 0 10px 0; color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px;">{station.get('name', 'Nieznana stacja')}</h4>
                                <p style="margin: 5px 0;"><strong>Kod:</strong> {station.get('code', 'N/A')}</p>
                                <p style="margin: 5px 0;"><strong>Rzeka:</strong> {station.get('river', 'N/A')}</p>
                                <p style="margin: 5px 0;"><strong>Województwo:</strong> {station.get('wojewodztwo', 'N/A')}</p>
                                <p style="margin: 5px 0;"><strong>Status:</strong> <span style="color: {color}; font-weight: bold;">{status.upper()}</span></p>
                                <hr style="margin: 10px 0; border: none; border-top: 1px solid #ecf0f1;">
                                <p style="margin: 5px 0;"><strong>💧 Stan wody:</strong> {station.get('stan_wody', 'Brak danych')}</p>
                                <p style="margin: 5px 0;"><strong>🌊 Przepływ:</strong> {station.get('przeplyw', 'Brak danych')}</p>
                                <p style="margin: 5px 0; font-size: 0.9em; color: #7f8c8d;"><strong>🕒 Ostatnia aktualizacja:</strong><br>{station.get('ostatnia_aktualizacja', 'Brak danych')}</p>
                            </div>
                            """
                            
                            folium.Marker(
                                location=[lat, lon],
                                popup=folium.Popup(popup_html, max_width=300),
                                tooltip=f"{station.get('name', 'Nieznana stacja')} - {station.get('river', 'N/A')}",
                                icon=folium.Icon(
                                    color=color,
                                    icon=icon,
                                    prefix='fa'
                                )
                            ).add_to(marker_cluster)
                    except (ValueError, TypeError) as e:
                        print(f"Błąd przy dodawaniu markera dla stacji {station.get('name', 'Unknown')}: {e}")
                        continue
            except ImportError:
                print("MarkerCluster nie jest dostępny, używam zwykłych markerów")
                cluster_markers = False
        
        if not cluster_markers:
            # Dodaj markery bezpośrednio do mapy (bez klasterowania)
            for station in limited_stations:
                try:
                    lat = float(station.get('lat', 0))
                    lon = float(station.get('lon', 0))
                    
                    if lat != 0 and lon != 0:
                        # Określ kolor markera na podstawie statusu
                        status = station.get('status', 'unknown')
                        if status == 'alarm':
                            color = 'red'
                            icon = 'exclamation-triangle'
                        elif status == 'warning':
                            color = 'orange'
                            icon = 'exclamation-circle'
                        elif status == 'active':
                            color = 'green'
                            icon = 'tint'
                        else:
                            color = 'gray'
                            icon = 'question'
                        
                        # Utwórz popup z informacjami o stacji
                        popup_html = f"""
                        <div style="width: 280px; font-family: Arial, sans-serif;">
                            <h4 style="margin: 0 0 10px 0; color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px;">{station.get('name', 'Nieznana stacja')}</h4>
                            <p style="margin: 5px 0;"><strong>Kod:</strong> {station.get('code', 'N/A')}</p>
                            <p style="margin: 5px 0;"><strong>Rzeka:</strong> {station.get('river', 'N/A')}</p>
                            <p style="margin: 5px 0;"><strong>Województwo:</strong> {station.get('wojewodztwo', 'N/A')}</p>
                            <p style="margin: 5px 0;"><strong>Status:</strong> <span style="color: {color}; font-weight: bold;">{status.upper()}</span></p>
                            <hr style="margin: 10px 0; border: none; border-top: 1px solid #ecf0f1;">
                            <p style="margin: 5px 0;"><strong>💧 Stan wody:</strong> {station.get('stan_wody', 'Brak danych')}</p>
                            <p style="margin: 5px 0;"><strong>🌊 Przepływ:</strong> {station.get('przeplyw', 'Brak danych')}</p>
                            <p style="margin: 5px 0; font-size: 0.9em; color: #7f8c8d;"><strong>🕒 Ostatnia aktualizacja:</strong><br>{station.get('ostatnia_aktualizacja', 'Brak danych')}</p>
                        </div>
                        """
                        
                        folium.Marker(
                            location=[lat, lon],
                            popup=folium.Popup(popup_html, max_width=300),
                            tooltip=f"{station.get('name', 'Nieznana stacja')} - {station.get('river', 'N/A')}",
                            icon=folium.Icon(
                                color=color,
                                icon=icon,
                                prefix='fa'
                            )
                        ).add_to(m)
                except (ValueError, TypeError) as e:
                    print(f"Błąd przy dodawaniu markera dla stacji {station.get('name', 'Unknown')}: {e}")
                    continue
        
        # Informacja o ograniczeniu markerów
        if len(stations_data) > max_markers:
            print(f"Wyświetlono {max_markers} z {len(stations_data)} stacji dla lepszej wydajności")
    
    # Dodaj kontrolę pełnego ekranu (z obsługą błędów)
    try:
        from folium.plugins import Fullscreen
        Fullscreen().add_to(m)
    except Exception as e:
        print(f"Błąd przy dodawaniu Fullscreen: {e}")
    
    # Dodaj mini mapę (z obsługą błędów)
    try:
        from folium.plugins import MiniMap
        minimap = MiniMap(toggle_display=True)
        m.add_child(minimap)
    except Exception as e:
        print(f"Błąd przy dodawaniu MiniMap: {e}")
    
    # Dodaj skalę (z obsługą błędów)
    try:
        from folium.plugins import MeasureControl
        m.add_child(MeasureControl())
    except Exception as e:
        print(f"Błąd przy dodawaniu MeasureControl: {e}")
    
    return m


def display_map(stations_data: list, map_style: str = "OpenStreetMap", cluster_markers: bool = False, width: int = None, height: int = None, responsive: bool = True):
    """Wyświetl mapę w aplikacji Streamlit z responsywnym interfejsem"""
    if stations_data:
        # Automatyczne dostosowanie rozmiaru do ekranu jeśli nie podano
        if width is None:
            width = 1200 if responsive else 1000
        if height is None:
            height = 700 if responsive else 600
            
        # Utwórz mapę z ulepszonymi funkcjonalnościami
        stations_map = create_stations_map(stations_data, map_style, cluster_markers, responsive)
        
        # Wyświetl mapę z responsywnym kontenerem
        if responsive:
            # CSS z poprawkami z-index dla markerów Folium i optymalizacją pozycjonowania
            st.markdown("""
            <style>
            /* Optymalizacja pozycjonowania mapy */
            .stApp > div:first-child {
                padding-top: 0rem !important;
            }
            
            div[data-testid="stVerticalBlock"] > div:has(iframe[title="streamlit_folium.st_folium"]) {
                margin-top: -1rem !important;
                margin-bottom: 0rem !important;
            }
            
            /* Poprawki z-index dla markerów Folium */
            .folium-map {
                z-index: 1 !important;
                margin: 0 !important;
                padding: 0 !important;
            }
            
            .leaflet-marker-icon {
                z-index: 1000 !important;
            }
            
            .leaflet-marker-shadow {
                z-index: 999 !important;
            }
            
            .leaflet-popup {
                z-index: 1001 !important;
            }
            
            .leaflet-tooltip {
                z-index: 1002 !important;
            }
            
            /* Optymalizacja responsywności */
            iframe[title="streamlit_folium.st_folium"] {
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            </style>
            """, unsafe_allow_html=True)
            
            folium_static(stations_map, width=width, height=height)
        else:
            folium_static(stations_map, width=width, height=height)
        
        # Ulepszone informacje o mapie z dodatkowymi statystykami
        with st.expander("ℹ️ Informacje o mapie i funkcjonalności", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Statystyki stacji
                active_count = len([s for s in stations_data if s.get('status') != 'inactive'])
                warning_count = len([s for s in stations_data if s.get('status') == 'warning'])
                alarm_count = len([s for s in stations_data if s.get('status') == 'alarm'])
                
                st.markdown(f"""
                **📊 Statystyki stacji:**
                - 🏭 Łącznie: {len(stations_data)}
                - ✅ Aktywne: {active_count}
                - ⚠️ Ostrzeżenia: {warning_count}
                - 🚨 Alarmy: {alarm_count}
                """)
            
            with col2:
                st.markdown(f"""
                **🗺️ Konfiguracja mapy:**
                - Styl: {map_style}
                - Warstwy: {'Wielowarstwowa' if map_style == 'OpenStreetMap' else 'Pojedyncza'}
                - Auto-dopasowanie: Włączone
                - Optymalizacja: Włączona
                """)
            
            with col3:
                st.markdown("""
                **🎮 Kontrolki mapy:**
                - 🔍 Zoom: Kółko myszy lub +/-
                - 📱 Pełny ekran: Przycisk w prawym górnym rogu
                - 🗺️ Mini mapa: Przycisk w lewym dolnym rogu
                - 📏 Pomiary: Przycisk w lewym górnym rogu
                - 🔄 Warstwy: Menu w prawym górnym rogu
                """)
            
            # Dodatkowe informacje o funkcjonalnościach OSM
            st.markdown("""
            **🌍 Funkcjonalności OpenStreetMap:**
            - **Interaktywne markery**: Kliknij marker aby zobaczyć szczegółowe informacje o stacji
            - **Tooltips**: Najedź myszą na marker aby zobaczyć podstawowe informacje
            - **Warstwy map**: Przełączaj między różnymi stylami map w sidebarze
            - **Auto-dopasowanie**: Automatyczne centrowanie widoku na wybrane stacje
            - **Optymalizacja**: Zoptymalizowany interfejs dla lepszej wydajności
            - **Kontrolki**: Pełny ekran, mini mapa, pomiary odległości i powierzchni
            """)
    else:
        st.warning("⚠️ Brak danych stacji do wyświetlenia na mapie")
        st.info("💡 Spróbuj dostosować filtry lub zsynchronizować dane z IMGW")
