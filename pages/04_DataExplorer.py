import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from shared_utils import get_connection, quote_table
from ui_utils import render_page_header, render_instructions_block

render_page_header("Data Explorer PRO", "Group, aggregate & visualize any table")

render_instructions_block("""
- Select any table to explore.
- Apply filters, group by dimensions, aggregate numeric metrics.
- Build charts and optionally save derived tables.
""")

# Load tables
conn = get_connection()
tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn)
conn.close()

selected_table = st.selectbox("Select table to explore", tables["name"].tolist() if not tables.empty else ["No tables found"])

if selected_table != "No tables found":
    conn = get_connection()
    df = pd.read_sql(f"SELECT * FROM {quote_table(selected_table)}", conn)
    conn.close()

    st.write(f"Total rows: {len(df)}")
    st.dataframe(df.head())

    st.header("Apply Filters")
    filtered_df = df.copy()

    # Core filters for NFL datasets
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
    st.dataframe(filtered_df)

    st.header("Group & Aggregate")
    group_cols = [col for col in filtered_df.columns if filtered_df[col].nunique() < 100]

    if group_cols:
        group_col = st.selectbox("Group by column", group_cols)
        numeric_cols = filtered_df.select_dtypes(include=["number"]).columns.tolist()
        agg_col = st.selectbox("Aggregate numeric column", numeric_cols)
        agg_func = st.selectbox("Aggregation function", ["sum", "mean", "max", "min", "count"])

        grouped = filtered_df.groupby(group_col)[agg_col].agg(agg_func).reset_index()
        st.write(grouped)

        st.header("Chart Builder")
        chart_type = st.selectbox("Chart Type", ["Bar", "Line", "Pie"])
        if chart_type == "Bar":
            fig = px.bar(grouped, x=group_col, y=agg_col)
        elif chart_type == "Line":
            fig = px.line(grouped, x=group_col, y=agg_col)
        else:
            fig = px.pie(grouped, names=group_col, values=agg_col)

        st.plotly_chart(fig, use_container_width=True)

        # Save aggregated result
        new_table_name = st.text_input("Save Aggregated Table")
        if st.button("💾 Save Aggregated Table"):
            if new_table_name:
                conn = get_connection()
                grouped.to_sql(new_table_name, conn, if_exists="replace", index=False)
                conn.close()
                st.success(f"✅ Saved aggregated table '{new_table_name}'.")
            else:
                st.warning("Please enter a table name to save.")
