"""
Główny plik aplikacji Streamlit
"""
# -*- coding: utf-8 -*-
# @title Strona Główna

import streamlit as st
from flood_monitoring.ui.pages import home, hydro_stations, hydro_warnings
from datetime import datetime

# Konfiguracja strony
st.set_page_config(
    page_title="System Monitorowania Powodzi",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS dla lepszego wyglądu
st.markdown("""
<style>
    /* Ukryj tylko domyślną nawigację Streamlit multipage */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }
    
    /* Ukryj nawigację multipage - specyficzne klasy */
    .css-1544g2n {
        display: none !important;
    }
    
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    .metric-container {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #2a5298;
    }
    
    .stSelectbox > div > div {
        background-color: #f8f9fa;
    }
    
    .nav-item {
        padding: 0.5rem 1rem;
        margin: 0.2rem 0;
        border-radius: 5px;
        transition: all 0.3s ease;
    }
    
    .nav-item:hover {
        background-color: #e3f2fd;
        transform: translateX(5px);
    }
</style>
""", unsafe_allow_html=True)

# Sidebar z nawigacją
with st.sidebar:
    st.markdown("""
    <div class="main-header">
        <h2>🌊 System Monitorowania</h2>
        <p>Powodzi w Polsce</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Informacje o systemie
    st.markdown("### 📊 Status systemu")
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.success(f"🟢 System aktywny")
    st.info(f"🕐 Ostatnia aktualizacja: {current_time}")
    
    st.divider()
    
    # Nawigacja
    st.markdown("### 🧭 Nawigacja")
    
    pages = {
        "🏠 Strona Główna": "Strona Główna",
        "🗺️ Mapa Stacji Pomiarowych": "Mapa Stacji Pomiarowych",
        "⚠️ Mapa Ostrzeżeń Hydrologicznych": "Mapa Ostrzeżeń Hydrologicznych"
    }
    
    page = st.radio(
        "Wybierz stronę:",
        list(pages.keys()),
        index=0,
        label_visibility="collapsed"
    )
    
    st.divider()
    
    # Szybkie akcje
    st.markdown("### ⚡ Szybkie akcje")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Odśwież", use_container_width=True):
            st.rerun()
    
    with col2:
        if st.button("📊 API Status", use_container_width=True):
            st.info("API działa poprawnie")
    
    # Test połączenia z proxy
    st.markdown("### 🔧 Narzędzia diagnostyczne")
    
    if st.button("🌐 Test curl -x (Proxy)", use_container_width=True, help="Wykonaj test połączenia z API przez proxy"):
        import subprocess
        import os
        
        try:
            # Pobierz URL backendu
            backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
            
            # Wykonaj curl z opcją proxy (używamy domyślnego proxy systemowego)
            result = subprocess.run(
                ["curl", "-x", "http://localhost:8080", "-s", "-w", "HTTP Status: %{http_code}\n", f"{backend_url}/stations/"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                st.success("✅ Test curl -x zakończony pomyślnie")
                with st.expander("📋 Szczegóły odpowiedzi"):
                    st.code(result.stdout, language="json")
            else:
                st.warning("⚠️ Test curl -x bez proxy...")
                # Fallback - test bez proxy
                result_fallback = subprocess.run(
                    ["curl", "-s", "-w", "HTTP Status: %{http_code}\n", f"{backend_url}/stations/"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result_fallback.returncode == 0:
                    st.success("✅ Połączenie bezpośrednie działa")
                    with st.expander("📋 Szczegóły odpowiedzi"):
                        st.code(result_fallback.stdout, language="json")
                else:
                    st.error("❌ Błąd połączenia z API")
                    st.code(result_fallback.stderr)
                    
        except subprocess.TimeoutExpired:
            st.error("⏱️ Timeout - połączenie trwało zbyt długo")
        except Exception as e:
            st.error(f"❌ Błąd podczas wykonywania curl: {str(e)}")
    
    # Informacje o aplikacji
    with st.expander("ℹ️ O aplikacji", expanded=False):
        st.markdown("""
        **Wersja:** 2.5  
        **Ostatnia aktualizacja:** 2025-09-03  
        **Źródło danych:** IMGW-PIB  
        **Technologie:** Python, Streamlit, FastAPI
        
        **Zespół deweloperski:**
        - Konrad Rybak (Skibidi)
        - Radosław Beta (Sigma)
        """)

# Wyświetl wybraną stronę
selected_page = pages[page]

if selected_page == "Strona Główna":
    home.show_home()
elif selected_page == "Mapa Stacji Pomiarowych":
    hydro_stations.show_hydro_stations()
elif selected_page == "Mapa Ostrzeżeń Hydrologicznych":
    hydro_warnings.show_hydro_warnings()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>🌊 System Monitorowania Powodzi | Dane z <a href="https://imgw.pl" target="_blank">IMGW-PIB</a> | 
    Utworzono z ❤️ przy użyciu Streamlit</p>
</div>
""", unsafe_allow_html=True)
