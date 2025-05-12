"""
Główny plik aplikacji Streamlit
"""
# -*- coding: utf-8 -*-
# @title Strona Główna

import streamlit as st

home_page = st.Page("pages/home.py", title="Strona Główna", icon="🏠", default=True)
map_page = st.Page("pages/hydro_stations.py", title="Mapa Stacji Pomiarowych", icon="🌊")

# Budujemy nawigację w sidebarze:
pages = [home_page, map_page]
selected = st.navigation(pages)

# (Opcjonalnie) ustalamy tytuł zakładki przeglądarki:
st.set_page_config(page_title="Flood Monitoring", page_icon="💧", layout="wide")

# Wykonujemy wybraną stronę:
selected.run()
