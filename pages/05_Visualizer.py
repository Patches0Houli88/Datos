import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from shared_utils import get_connection, quote_table
from ui_utils import render_page_header, render_instructions_block, render_kpi_cards
from filter_utils import apply_universal_filters

render_page_header("Dashboard Visualizer PRO v4", "Build dashboards with unified filters")

render_instructions_block("""
- Apply universal filters: Season, Player, Position.
- Auto-generates KPI cards and key charts.
- Fully powered by fantasy_points_ppr.
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
    filtered_df = apply_universal_filters(df)
    st.dataframe(filtered_df)

    st.header("KPI Summary")

    total_pts = round(filtered_df.get("fantasy_points_ppr", pd.Series()).sum(), 2)
    avg_ppg = round(filtered_df.get("fantasy_points_ppr", pd.Series()).mean(), 2)
    unique_players = filtered_df.get("player_name", pd.Series()).nunique()

    render_kpi_cards([
        ("Total Fantasy Points (PPR)", total_pts, None),
        ("Avg Points Per Game", avg_ppg, None),
        ("Unique Players", unique_players, None),
    ])

    st.header("Visualizations")

    # Top Players by PPR
    if "player_name" in filtered_df.columns:
        player_summary = filtered_df.groupby("player_name")["fantasy_points_ppr"].sum().reset_index()
        player_summary = player_summary.sort_values(by="fantasy_points_ppr", ascending=False).head(20)
        fig1 = px.bar(player_summary, x="player_name", y="fantasy_points_ppr", title="Top Players (PPR Total)")
        st.plotly_chart(fig1, use_container_width=True)

    # Position Breakdown Pie
    if "position" in filtered_df.columns:
        pos_summary = filtered_df["position"].value_counts().reset_index()
        pos_summary.columns = ["position", "count"]
        fig2 = px.pie(pos_summary, names="position", values="count", title="Position Breakdown")
        st.plotly_chart(fig2, use_container_width=True)

    # Weekly Fantasy Trend
    if "week" in filtered_df.columns and "fantasy_points_ppr" in filtered_df.columns:
        weekly = filtered_df.groupby("week")["fantasy_points_ppr"].sum().reset_index()
        fig3 = px.line(weekly, x="week", y="fantasy_points_ppr", markers=True, title="Weekly Total Fantasy Points (PPR)")
        st.plotly_chart(fig3, use_container_width=True)
