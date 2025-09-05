"""Komponenty do wizualizacji danych hydrologicznych"""
from typing import Any, Dict, List
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from datetime import datetime, timedelta
import hashlib
import json


@st.cache_data(ttl=300)  # Cache na 5 minut
def create_water_level_chart(data: Dict[str, List[Dict[str, Any]]], station_name: str = "") -> go.Figure:
    """Utwórz zaawansowany wykres poziomu wody z trendami i alertami"""
    if not data.get("stan"):
        return None

    df = pd.DataFrame(data["stan"])
    df["stan_wody_data_pomiaru"] = pd.to_datetime(df["stan_wody_data_pomiaru"])
    df = df.sort_values("stan_wody_data_pomiaru")
    
    # Oblicz statystyki
    mean_level = df["stan_wody"].mean()
    std_level = df["stan_wody"].std()
    max_level = df["stan_wody"].max()
    min_level = df["stan_wody"].min()
    
    # Utwórz wykres
    fig = go.Figure()
    
    # Główna linia poziomu wody
    fig.add_trace(go.Scatter(
        x=df["stan_wody_data_pomiaru"],
        y=df["stan_wody"],
        mode='lines+markers',
        name='Poziom wody',
        line=dict(color='#1f77b4', width=2),
        marker=dict(size=4),
        hovertemplate='<b>Data:</b> %{x}<br><b>Poziom:</b> %{y} cm<extra></extra>'
    ))
    
    # Linia średniej
    fig.add_hline(
        y=mean_level, 
        line_dash="dash", 
        line_color="green",
        annotation_text=f"Średnia: {mean_level:.1f} cm",
        annotation_position="top right"
    )
    
    # Strefy ostrzeżeń (przykładowe wartości)
    if max_level > mean_level + 2 * std_level:
        fig.add_hline(
            y=mean_level + 2 * std_level,
            line_dash="dot",
            line_color="orange",
            annotation_text="Ostrzeżenie",
            annotation_position="top left"
        )
    
    if max_level > mean_level + 3 * std_level:
        fig.add_hline(
            y=mean_level + 3 * std_level,
            line_dash="dot",
            line_color="red",
            annotation_text="Alarm",
            annotation_position="top left"
        )
    
    # Trend (regresja liniowa)
    if len(df) > 2:
        x_numeric = pd.to_numeric(df["stan_wody_data_pomiaru"])
        z = np.polyfit(x_numeric, df["stan_wody"], 1)
        trend_line = np.poly1d(z)(x_numeric)
        
        fig.add_trace(go.Scatter(
            x=df["stan_wody_data_pomiaru"],
            y=trend_line,
            mode='lines',
            name='Trend',
            line=dict(color='red', width=1, dash='dash'),
            opacity=0.7
        ))
    
    fig.update_layout(
        title=f" Poziom wody - {station_name}" if station_name else " Poziom wody",
        xaxis_title="Data i czas",
        yaxis_title="Poziom wody [cm]",
        hovermode='x unified',
        showlegend=True,
        template='plotly_white',
        height=400
    )
    
    return fig


@st.cache_data(ttl=300)  # Cache na 5 minut
def create_flow_chart(data: Dict[str, List[Dict[str, Any]]], station_name: str = "") -> go.Figure:
    """Utwórz zaawansowany wykres przepływu z analizą statystyczną"""
    if not data.get("przelyw"):
        return None

    df = pd.DataFrame(data["przelyw"])
    df["przeplyw_data"] = pd.to_datetime(df["przeplyw_data"])
    df = df.sort_values("przeplyw_data")
    
    # Oblicz statystyki
    mean_flow = df["przelyw"].mean()
    median_flow = df["przelyw"].median()
    q75 = df["przelyw"].quantile(0.75)
    q25 = df["przelyw"].quantile(0.25)
    
    fig = go.Figure()
    
    # Główna linia przepływu z wypełnieniem
    fig.add_trace(go.Scatter(
        x=df["przeplyw_data"],
        y=df["przelyw"],
        mode='lines+markers',
        name='Przepływ',
        line=dict(color='#2ca02c', width=2),
        marker=dict(size=4),
        fill='tonexty',
        fillcolor='rgba(44, 160, 44, 0.1)',
        hovertemplate='<b>Data:</b> %{x}<br><b>Przepływ:</b> %{y} m³/s<extra></extra>'
    ))
    
    # Linie statystyczne
    fig.add_hline(
        y=mean_flow,
        line_dash="dash",
        line_color="blue",
        annotation_text=f"Średnia: {mean_flow:.2f} m³/s",
        annotation_position="top right"
    )
    
    fig.add_hline(
        y=median_flow,
        line_dash="dot",
        line_color="purple",
        annotation_text=f"Mediana: {median_flow:.2f} m³/s",
        annotation_position="bottom right"
    )
    
    # Strefy kwartylowe
    fig.add_hrect(
        y0=q25, y1=q75,
        fillcolor="rgba(128, 128, 128, 0.1)",
        line_width=0,
        annotation_text="Q1-Q3",
        annotation_position="top left"
    )
    
    fig.update_layout(
        title=f" Przepływ - {station_name}" if station_name else " Przepływ",
        xaxis_title="Data i czas",
        yaxis_title="Przepływ [m³/s]",
        hovermode='x unified',
        showlegend=True,
        template='plotly_white',
        height=400
    )
    
    return fig


def display_station_charts(data: Dict[str, List[Dict[str, Any]]], station_name: str = ""):
    """Wyświetl zaawansowane wykresy dla stacji z dodatkowymi analizami"""
    try:
        has_water_data = bool(data.get("stan"))
        has_flow_data = bool(data.get("przelyw"))
        
        if not has_water_data and not has_flow_data:
            st.warning("️ Brak danych dla wybranej stacji")
            return

        if station_name:
            st.subheader(f" Analiza danych - {station_name}")

        if has_water_data or has_flow_data:
            col1, col2, col3, col4 = st.columns(4)
            
            if has_water_data:
                water_df = pd.DataFrame(data["stan"])
                latest_water = water_df.iloc[-1]["stan_wody"] if len(water_df) > 0 else 0
                avg_water = water_df["stan_wody"].mean() if len(water_df) > 0 else 0
                
                with col1:
                    st.metric(
                        " Aktualny poziom",
                        f"{latest_water:.1f} cm",
                        delta=f"{latest_water - avg_water:.1f} cm od średniej"
                    )
                
                with col2:
                    st.metric(
                        " Średni poziom",
                        f"{avg_water:.1f} cm",
                        help="Średni poziom wody w analizowanym okresie"
                    )
            
            if has_flow_data:
                flow_df = pd.DataFrame(data["przelyw"])
                latest_flow = flow_df.iloc[-1]["przelyw"] if len(flow_df) > 0 else 0
                avg_flow = flow_df["przelyw"].mean() if len(flow_df) > 0 else 0
                
                with col3:
                    st.metric(
                        " Aktualny przepływ",
                        f"{latest_flow:.2f} m³/s",
                        delta=f"{latest_flow - avg_flow:.2f} m³/s od średniej"
                    )
                
                with col4:
                    st.metric(
                        " Średni przepływ",
                        f"{avg_flow:.2f} m³/s",
                        help="Średni przepływ w analizowanym okresie"
                    )

        if has_water_data and has_flow_data:
            col1, col2 = st.columns(2)
            
            with col1:
                water_level_fig = create_water_level_chart(data, station_name)
                if water_level_fig:
                    st.plotly_chart(water_level_fig, use_container_width=True)
            
            with col2:
                flow_fig = create_flow_chart(data, station_name)
                if flow_fig:
                    st.plotly_chart(flow_fig, use_container_width=True)
        else:
            if has_water_data:
                water_level_fig = create_water_level_chart(data, station_name)
                if water_level_fig:
                    st.plotly_chart(water_level_fig, use_container_width=True)
                else:
                    st.info(" Brak danych o poziomie wody")
            if has_flow_data:
                flow_fig = create_flow_chart(data, station_name)
                if flow_fig:
                    st.plotly_chart(flow_fig, use_container_width=True)
                else:
                    st.info(" Brak danych o przepływie")

        st.markdown("###  Szczegółowa analiza statystyczna")
        col1, col2 = st.columns(2)
        
        if has_water_data:
            with col1:
                st.markdown("** Poziom wody:**")
                water_df = pd.DataFrame(data["stan"])
                st.write(f"• Minimum: {water_df['stan_wody'].min():.1f} cm")
                st.write(f"• Maksimum: {water_df['stan_wody'].max():.1f} cm")
                st.write(f"• Odchylenie std: {water_df['stan_wody'].std():.1f} cm")
                st.write(f"• Liczba pomiarów: {len(water_df)}")
        
        if has_flow_data:
            with col2:
                st.markdown("** Przepływ:**")
                flow_df = pd.DataFrame(data["przelyw"])
                st.write(f"• Minimum: {flow_df['przelyw'].min():.2f} m³/s")
                st.write(f"• Maksimum: {flow_df['przelyw'].max():.2f} m³/s")
                st.write(f"• Odchylenie std: {flow_df['przelyw'].std():.2f} m³/s")
                st.write(f"• Liczba pomiarów: {len(flow_df)}")

    except Exception as e:
        st.error(f"❌ Błąd podczas przetwarzania danych: {str(e)}")
        st.markdown("** Szczegóły błędu (dla deweloperów):**")
        st.write("Raw data:", data)
        st.exception(e)


@st.cache_data(ttl=300)
def create_comparison_chart(stations_data: Dict[str, Dict]) -> go.Figure:
    """Utwórz zaawansowany wykres porównawczy poziomów wody dla wielu stacji"""
    if not stations_data:
        return None

    fig = go.Figure()
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']
    
    station_stats = {}
    
    for i, (station_name, data) in enumerate(stations_data.items()):
        if data.get("stan"):
            df = pd.DataFrame(data["stan"])
            df["stan_wody_data_pomiaru"] = pd.to_datetime(df["stan_wody_data_pomiaru"])
            df = df.sort_values("stan_wody_data_pomiaru")

            mean_level = df["stan_wody"].mean()
            max_level = df["stan_wody"].max()
            min_level = df["stan_wody"].min()
            station_stats[station_name] = {'mean': mean_level, 'max': max_level, 'min': min_level}
            
            color = colors[i % len(colors)]

            fig.add_trace(
                go.Scatter(
                    x=df["stan_wody_data_pomiaru"],
                    y=df["stan_wody"],
                    mode="lines+markers",
                    name=f"{station_name} (śr: {mean_level:.1f}cm)",
                    marker=dict(size=4),
                    line=dict(color=color, width=2),
                    hovertemplate=f'<b>{station_name}</b><br>Data: %{{x}}<br>Poziom: %{{y}} cm<extra></extra>'
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=df["stan_wody_data_pomiaru"],
                    y=[mean_level] * len(df),
                    mode="lines",
                    name=f"{station_name} - średnia",
                    line=dict(color=color, width=1, dash='dash'),
                    opacity=0.5,
                    showlegend=False,
                    hovertemplate=f'<b>{station_name} - średnia</b><br>%{{y:.1f}} cm<extra></extra>'
                )
            )

    fig.update_layout(
        title=" Porównanie poziomów wody między stacjami",
        xaxis_title="Data i czas",
        yaxis_title="Poziom wody [cm]",
        hovermode="x unified",
        template='plotly_white',
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig


@st.cache_data(ttl=300)
def create_flow_comparison_chart(stations_data: Dict[str, Dict]) -> go.Figure:
    """Utwórz zaawansowany wykres porównawczy przepływów dla wielu stacji"""
    if not stations_data:
        return None

    fig = go.Figure()
    colors = ['#2ca02c', '#ff7f0e', '#1f77b4', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']
    
    station_stats = {}
    
    for i, (station_name, data) in enumerate(stations_data.items()):
        if data.get("przelyw"):
            df = pd.DataFrame(data["przelyw"])
            df["przeplyw_data"] = pd.to_datetime(df["przeplyw_data"])
            df = df.sort_values("przeplyw_data")

            mean_flow = df["przelyw"].mean()
            max_flow = df["przelyw"].max()
            min_flow = df["przelyw"].min()
            station_stats[station_name] = {'mean': mean_flow, 'max': max_flow, 'min': min_flow}
            
            color = colors[i % len(colors)]

            fig.add_trace(
                go.Scatter(
                    x=df["przeplyw_data"],
                    y=df["przelyw"],
                    mode="lines+markers",
                    name=f"{station_name} (śr: {mean_flow:.2f}m³/s)",
                    marker=dict(size=4),
                    line=dict(color=color, width=2),
                    fill='tonexty' if i > 0 else None,
                    fillcolor=f'rgba{tuple(list(px.colors.hex_to_rgb(color)) + [0.1])}' if i > 0 else None,
                    hovertemplate=f'<b>{station_name}</b><br>Data: %{{x}}<br>Przepływ: %{{y}} m³/s<extra></extra>'
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=df["przeplyw_data"],
                    y=[mean_flow] * len(df),
                    mode="lines",
                    name=f"{station_name} - średnia",
                    line=dict(color=color, width=1, dash='dot'),
                    opacity=0.6,
                    showlegend=False,
                    hovertemplate=f'<b>{station_name} - średnia</b><br>%{{y:.2f}} m³/s<extra></extra>'
                )
            )

    fig.update_layout(
        title=" Porównanie przepływów między stacjami",
        xaxis_title="Data i czas",
        yaxis_title="Przepływ [m³/s]",
        hovermode="x unified",
        template='plotly_white',
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig
