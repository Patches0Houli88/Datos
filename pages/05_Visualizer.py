import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from shared_utils import get_connection, quote_table
from ui_utils import render_page_header, render_instructions_block, render_kpi_cards

render_page_header("Dashboard Visualizer PRO", "📊 Build full dashboards for any dataset")

render_instructions_block("""
- Select any table to build your dashboard.
- Apply filters and generate KPI metrics automatically.
- Create multiple charts for players, positions, teams, and fantasy points.
- Fully compatible with saved Search + Explorer tables.
""")

# Load tables
conn = get_connection()
tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn)
conn.close()

selected_table = st.selectbox("Select dataset for dashboard", tables["name"].tolist() if not tables.empty else ["No tables found"])

if selected_table != "No tables found":
    conn = get_connection()
    df = pd.read_sql(f"SELECT * FROM {quote_table(selected_table)}", conn)
    conn.close()

    st.write(f"Total rows: {len(df)}")
    st.dataframe(df.head())

    st.header("Apply Filters")
    filtered_df = df.copy()

    if "season" in df.columns:
        seasons = sorted(df["season"].dropna().unique())
        season_range = st.slider("Season Range", min(seasons), max(seasons), (min(seasons), max(seasons)))
        filtered_df = filtered_df[filtered_df["season"].between(*season_range)]

    if "week" in df.columns:
        weeks = sorted(df["week"].dropna().unique())
        week_range = st.slider("Week Range", min(weeks), max(weeks), (min(weeks), max(weeks)))
        filtered_df = filtered_df[filtered_df["week"].between(*week_range)]

    if "position" in df.columns:
        positions = sorted(df["position"].dropna().unique())
        selected_positions = st.multiselect("Position", positions, default=positions)
        filtered_df = filtered_df[filtered_df["position"].isin(selected_positions)]

    if "player_name" in df.columns:
        player_search = st.text_input("Search by Player Name")
        if player_search:
            filtered_df = filtered_df[filtered_df["player_name"].str.contains(player_search, case=False, na=False)]

    st.write(f"Filtered rows: {len(filtered_df)}")

    st.header("Fantasy KPI Summary")

    # Auto Fantasy KPIs
    total_pts = round(filtered_df.get("fantasy_points", pd.Series()).sum(), 2)
    avg_ppg = round(filtered_df.get("fantasy_points", pd.Series()).mean(), 2)
    unique_players = filtered_df.get("player_name", pd.Series()).nunique()

    render_kpi_cards([
        ("Total Fantasy Points", total_pts, None),
        ("Avg Points Per Game", avg_ppg, None),
        ("Unique Players", unique_players, None),
    ])

    st.header("Visualizations")

    # Player Distribution Chart
    if "player_name" in filtered_df.columns:
        player_summary = filtered_df.groupby("player_name")["fantasy_points"].sum().reset_index()
        player_summary = player_summary.sort_values(by="fantasy_points", ascending=False).head(20)
        fig1 = px.bar(player_summary, x="player_name", y="fantasy_points", title="Top Players by Fantasy Points")
        st.plotly_chart(fig1, use_container_width=True)

    # Position Breakdown Pie
    if "position" in filtered_df.columns:
        pos_summary = filtered_df["position"].value_counts().reset_index()
        pos_summary.columns = ["position", "count"]
        fig2 = px.pie(pos_summary, names="position", values="count", title="Position Breakdown")
        st.plotly_chart(fig2, use_container_width=True)

    # Weekly Fantasy Trend
    if "week" in filtered_df.columns and "fantasy_points" in filtered_df.columns:
        weekly = filtered_df.groupby("week")["fantasy_points"].sum().reset_index()
        fig3 = px.line(weekly, x="week", y="fantasy_points", markers=True, title="Weekly Total Fantasy Points")
        st.plotly_chart(fig3, use_container_width=True)
