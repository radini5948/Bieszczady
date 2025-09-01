"""
Komponenty do wizualizacji danych hydrologicznych
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
    df["stan_wody_data_pomiaru"] = pd.to_datetime(df["stan_wody_data_pomiaru"])
    df = df.sort_values("stan_wody_data_pomiaru")

    fig = px.line(
        df,
        x="stan_wody_data_pomiaru",
        y="stan_wody",
        title="Poziom wody",
        labels={"stan_wody_data_pomiaru": "Data", "stan_wody": "Poziom wody [cm]"},
    )
    fig.update_traces(mode="lines+markers")
    return fig


def create_flow_chart(data: Dict[str, List[Dict[str, Any]]]) -> go.Figure:
    """Utwórz wykres przepływu"""
    if not data.get("przelyw"):
        return None

    df = pd.DataFrame(data["przelyw"])
    df["przeplyw_data"] = pd.to_datetime(df["przeplyw_data"])
    df = df.sort_values("przeplyw_data")

    fig = px.line(
        df,
        x="przeplyw_data",
        y="przelyw",
        title="Przepływ",
        labels={"przeplyw_data": "Data", "przelyw": "Przepływ [m³/s]"},
    )
    fig.update_traces(mode="lines+markers")
    return fig


def display_station_charts(data: Dict[str, List[Dict[str, Any]]]):
    """Wyświetl wykresy dla stacji"""
    try:
        water_level_fig = create_water_level_chart(data)
        if water_level_fig:
            st.plotly_chart(water_level_fig, use_container_width=True)
        else:
            st.info("Brak danych o poziomie wody")

        flow_fig = create_flow_chart(data)
        if flow_fig:
            st.plotly_chart(flow_fig, use_container_width=True)
        else:
            st.info("Brak danych o przepływie")

    except Exception as e:
        st.error(f"Błąd podczas przetwarzania danych: {str(e)}")
        st.write("Raw data:", data)


def create_comparison_chart(stations_data: Dict[str, Dict]) -> go.Figure:
    """Porównaj poziom wody dla wielu stacji"""
    fig = go.Figure()

    for station_name, data in stations_data.items():
        if not data.get("stan"):
            continue
        df = pd.DataFrame(data["stan"])
        df["stan_wody_data_pomiaru"] = pd.to_datetime(df["stan_wody_data_pomiaru"])
        df = df.sort_values("stan_wody_data_pomiaru")

        fig.add_trace(
            go.Scatter(
                x=df["stan_wody_data_pomiaru"],
                y=df["stan_wody"],
                mode="lines+markers",
                name=station_name
            )
        )

    fig.update_layout(
        title="Porównanie poziomu wody",
        xaxis_title="Data",
        yaxis_title="Poziom wody [cm]"
    )
    return fig


def create_flow_comparison_chart(stations_data: Dict[str, Dict]) -> go.Figure:
    """Porównaj przepływy dla wielu stacji"""
    fig = go.Figure()

    for station_name, data in stations_data.items():
        if not data.get("przelyw"):
            continue
        df = pd.DataFrame(data["przelyw"])
        df["przeplyw_data"] = pd.to_datetime(df["przeplyw_data"])
        df = df.sort_values("przeplyw_data")

        fig.add_trace(
            go.Scatter(
                x=df["przeplyw_data"],
                y=df["przelyw"],
                mode="lines+markers",
                name=station_name
            )
        )

    fig.update_layout(
        title="Porównanie przepływów",
        xaxis_title="Data",
        yaxis_title="Przepływ [m³/s]"
    )
    return fig
