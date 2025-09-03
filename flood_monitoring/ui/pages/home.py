import streamlit as st
import requests
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import os

# Pobierz URL backendu z zmiennej środowiskowej
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def show_home():
    """Wyświetl stronę główną aplikacji"""
    
    # Custom CSS dla lepszego wyglądu
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #667eea 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.2rem;
        opacity: 0.9;
    }
    
    /* Cursor */
    .cursor {
        position: relative;
        margin: 0 auto;
        border-right: 2px solid rgba(255,255,255,.75);
        text-align: center;
        white-space: nowrap;
        overflow: hidden;
    }
    
    .cursor-h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
    }
    
    .cursor-p {
        font-size: 1.2rem;
        opacity: 0.9;
        margin: 0.5rem 0 0 0;
    }
    
    /* Animation */
    .typewriter-animation-h1 {
        animation: 
            typewriter-h1 4.5s steps(40) 0s 1 normal both,
            blinkingCursor 500ms steps(2) infinite normal;
    }
    
    .typewriter-animation-p {
        animation: 
            typewriter-p 3.5s steps(50) 4.8s 1 normal both;
    }
    
    .no-cursor {
        border-right: none !important;
    }
    
    @keyframes typewriter-h1 {
        from { width: 0; }
        to { width: 100%; }
    }
    
    @keyframes typewriter-p {
        from { width: 0; opacity: 1; }
        to { width: 100%; opacity: 1; }
    }
    
    @keyframes blinkingCursor {
        from { border-right-color: rgba(255,255,255,.75); }
        to { border-right-color: transparent; }
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #667eea;
    }
    
    .metric-label {
        color: #666;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    
    .feature-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e9ecef;
        height: 100%;
        color: #212529;
    }
    .feature-card h4 {
        color: #2a5298;
        margin-bottom: 1rem;
    }
    .feature-card p {
        color: #495057;
        margin-bottom: 1rem;
    }
    .feature-card ul {
        color: #495057;
    }
    .feature-card li {
        color: #495057;
        margin-bottom: 0.25rem;
    }
    .alert-box {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .status-card {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

    # Nagłówek główny
    st.markdown("""
    <div class="main-header">
        <h1 class="cursor cursor-h1 typewriter-animation-h1">🌊 System Monitorowania Zagrożeń Powodziowych</h1>
        <p class="cursor cursor-p typewriter-animation-p no-cursor">Kompleksowe narzędzie do monitorowania stanu wód w Polsce</p>
    </div>
    """, unsafe_allow_html=True)

    # Dashboard z metrykami
    st.subheader("📊 Dashboard systemu")
    
    # Pobierz dane z API (z obsługą błędów)
    try:
        # Liczba stacji
        stations_response = requests.get(f"{BACKEND_URL}/stations/", timeout=5)
        if stations_response.status_code == 200:
            stations_data = stations_response.json()
            # Pobierz liczbę stacji z tablicy 'features' w GeoJSON
            stations_count = len(stations_data.get('features', []))
        else:
            stations_count = "N/A"
    except:
        stations_count = "N/A"
    
    try:
        # Liczba ostrzeżeń
        warnings_response = requests.get(f"{BACKEND_URL}/warnings/", timeout=5)
        warnings_count = len(warnings_response.json()) if warnings_response.status_code == 200 else "N/A"
    except:
        warnings_count = "N/A"
    
    # Wyświetl metryki
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🏭 Stacje pomiarowe",
            value=stations_count,
            help="Łączna liczba stacji hydrologicznych w systemie"
        )
    
    with col2:
        st.metric(
            label="⚠️ Aktywne ostrzeżenia",
            value=warnings_count,
            help="Liczba aktywnych ostrzeżeń hydrologicznych"
        )
    
    with col3:
        st.metric(
            label="🕐 Ostatnia aktualizacja",
            value=datetime.now().strftime("%H:%M"),
            help="Czas ostatniej aktualizacji danych"
        )
    
    with col4:
        st.metric(
            label="📡 Status systemu",
            value="🟢 Aktywny",
            help="Aktualny status działania systemu"
        )
    
    st.divider()
    
    # Sekcja funkcji
    st.subheader("🚀 Funkcje systemu")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h4>🗺️ Mapa stacji pomiarowych</h4>
            <p>Interaktywna mapa z lokalizacjami wszystkich stacji hydrologicznych w Polsce. 
            Możliwość filtrowania według województw, rzek i statusu stacji.</p>
            <ul>
                <li>📍 Lokalizacje stacji</li>
                <li>📊 Dane pomiarowe</li>
                <li>📈 Wykresy trendów</li>
                <li>🔍 Zaawansowane filtry</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h4>⚠️ Mapa ostrzeżeń hydrologicznych</h4>
            <p>Wizualizacja aktualnych ostrzeżeń hydrologicznych z podziałem na województwa. 
            Kolorowe oznaczenia według poziomu zagrożenia.</p>
            <ul>
                <li>🟡 Ostrzeżenia 1. stopnia</li>
                <li>🟠 Ostrzeżenia 2. stopnia</li>
                <li>🔴 Ostrzeżenia 3. stopnia</li>
                <li>📋 Szczegółowe informacje</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h4>📊 Analiza danych</h4>
            <p>Zaawansowane narzędzia do analizy danych hydrologicznych. 
            Porównania między stacjami i analiza trendów czasowych.</p>
            <ul>
                <li>📈 Wykresy interaktywne</li>
                <li>📉 Analiza statystyczna</li>
                <li>🔄 Porównania stacji</li>
                <li>💾 Eksport danych</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Szybkie akcje
    st.subheader("⚡ Szybkie akcje")
    
    # Inicjalizacja session state dla zarządzania stanem przycisków
    if 'sync_in_progress' not in st.session_state:
        st.session_state.sync_in_progress = False
    if 'last_action_time' not in st.session_state:
        st.session_state.last_action_time = 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    def safe_api_call(url, method='GET', timeout=30, action_name="operacja"):
        """Bezpieczne wywołanie API z obsługą błędów i debouncing"""
        import time
        
        current_time = time.time()
        # Debouncing - zapobieganie zbyt szybkim kliknięciom (min 1 sekunda między akcjami)
        if current_time - st.session_state.last_action_time < 1.0:
            st.warning(f"⏳ Poczekaj chwilę przed kolejną akcją ({action_name})")
            return None
            
        st.session_state.last_action_time = current_time
        st.session_state.sync_in_progress = True
        
        try:
            if method == 'POST':
                response = requests.post(url, timeout=timeout)
            else:
                response = requests.get(url, timeout=timeout)
            
            st.session_state.sync_in_progress = False
            return response
            
        except requests.exceptions.Timeout:
            st.session_state.sync_in_progress = False
            st.error(f"⏰ Przekroczono limit czasu dla {action_name}")
            return None
        except requests.exceptions.ConnectionError:
            st.session_state.sync_in_progress = False
            st.error(f"🔌 Błąd połączenia z API podczas {action_name}")
            return None
        except requests.exceptions.RequestException as e:
            st.session_state.sync_in_progress = False
            st.error(f"❌ Błąd żądania podczas {action_name}: {str(e)}")
            return None
        except Exception as e:
            st.session_state.sync_in_progress = False
            st.error(f"❌ Nieoczekiwany błąd podczas {action_name}: {str(e)}")
            return None
    
    with col1:
        if st.button("🔄 Synchronizuj wszystkie dane", use_container_width=True, disabled=st.session_state.sync_in_progress):
            with st.spinner("Synchronizacja w toku..."):
                response = safe_api_call(f"{BACKEND_URL}/sync/all/", method='POST', timeout=30, action_name="synchronizacji wszystkich danych")
                if response and response.status_code == 200:
                    st.success("✅ Synchronizacja zakończona pomyślnie")
                elif response:
                    st.error(f"❌ Błąd podczas synchronizacji (kod: {response.status_code})")
    
    with col2:
        if st.button("🏭 Synchronizuj stacje", use_container_width=True, disabled=st.session_state.sync_in_progress):
            with st.spinner("Synchronizacja stacji..."):
                response = safe_api_call(f"{BACKEND_URL}/sync/stations/", method='POST', timeout=15, action_name="synchronizacji stacji")
                if response and response.status_code == 200:
                    st.success("✅ Stacje zsynchronizowane")
                elif response:
                    st.error(f"❌ Błąd synchronizacji stacji (kod: {response.status_code})")
    
    with col3:
        if st.button("⚠️ Synchronizuj ostrzeżenia", use_container_width=True, disabled=st.session_state.sync_in_progress):
            with st.spinner("Synchronizacja ostrzeżeń..."):
                response = safe_api_call(f"{BACKEND_URL}/sync/warnings/", method='POST', timeout=10, action_name="synchronizacji ostrzeżeń")
                if response and response.status_code == 200:
                    st.success("✅ Ostrzeżenia zsynchronizowane")
                elif response:
                    st.error(f"❌ Błąd synchronizacji ostrzeżeń (kod: {response.status_code})")
    
    with col4:
        if st.button("📊 Sprawdź status API", use_container_width=True, disabled=st.session_state.sync_in_progress):
            response = safe_api_call(f"{BACKEND_URL}/health/", method='GET', timeout=5, action_name="sprawdzania statusu API")
            if response and response.status_code == 200:
                st.success("✅ API działa prawidłowo")
            elif response:
                st.warning(f"⚠️ API odpowiada, ale może mieć problemy (kod: {response.status_code})")

    # Informacje o systemie
    with st.expander("ℹ️ Informacje o systemie", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **📋 O projekcie:**
            - System monitorowania zagrożeń powodziowych
            - Dane z Instytutu Meteorologii i Gospodarki Wodnej (IMGW)
            - Projekt na przedmiot Programowanie Aplikacji Geoinformatycznych
            
            **🔧 Technologie:**
            - Backend: FastAPI + PostgreSQL
            - Frontend: Streamlit
            - Mapy: Folium
            - Wykresy: Plotly
            """)
        
        with col2:
            st.markdown("""
            **📊 Źródła danych:**
            - IMGW-PIB (Instytut Meteorologii i Gospodarki Wodnej)
            - Dane hydrologiczne w czasie rzeczywistym
            - Ostrzeżenia meteorologiczne i hydrologiczne
            
            **🔄 Aktualizacja:**
            - Dane stacji: na żądanie
            - Ostrzeżenia: automatycznie
            - Pomiary: co 1 godzina (IMGW)
            """)

    # Stopka
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        💧 System Monitorowania Zagrożeń Powodziowych | Powered by IMGW-PIB | 
        <a href="http://localhost:8000/docs" target="_blank">📖 Dokumentacja API</a>
    </div>
    """, unsafe_allow_html=True)
