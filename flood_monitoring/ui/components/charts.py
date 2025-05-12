"""
Komponenty do wizualizacji danych
"""
from typing import Any, Dict, List

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def create_water_level_chart(data: Dict[str, List[Dict[str, Any]]]) -> go.Figure:
    """Utwórz wykres poziomu wody"""
    if not data.get("stan"):
        return None

    df = pd.DataFrame(data["stan"])
    df["stan_data"] = pd.to_datetime(df["stan_data"])
    df = df.sort_values("stan_data")  # Sortujemy po dacie

    fig = px.line(
        df,
        x="stan_data",
        y="stan",
        title="Poziom wody",
        labels={"stan_data": "Data", "stan": "Poziom wody [cm]"},
    )
    fig.update_traces(mode="lines+markers")
    return fig


def create_flow_chart(data: Dict[str, List[Dict[str, Any]]]) -> go.Figure:
    """Utwórz wykres przepływu"""
    if not data.get("przeplyw"):
        return None

    df = pd.DataFrame(data["przeplyw"])
    df["przeplyw_data"] = pd.to_datetime(df["przeplyw_data"])
    df = df.sort_values("przeplyw_data")  # Sortujemy po dacie

    fig = px.line(
        df,
        x="przeplyw_data",
        y="przeplyw",
        title="Przepływ",
        labels={"przeplyw_data": "Data", "przeplyw": "Przepływ [m³/s]"},
    )
    fig.update_traces(mode="lines+markers")
    return fig


def display_station_charts(data: Dict[str, List[Dict[str, Any]]]):
    """Wyświetl wykresy dla stacji"""
    try:
        # Wykres poziomu wody
        water_level_fig = create_water_level_chart(data)
        if water_level_fig:
            st.plotly_chart(water_level_fig, use_container_width=True)
        else:
            st.info("Brak danych o poziomie wody")

        # Wykres przepływu
        flow_fig = create_flow_chart(data)
        if flow_fig:
            st.plotly_chart(flow_fig, use_container_width=True)
        else:
            st.info("Brak danych o przepływie")

    except Exception as e:
        st.error(f"Error processing station data: {str(e)}")
        st.write("Raw data:", data)
