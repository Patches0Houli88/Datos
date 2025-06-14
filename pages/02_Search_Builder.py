import streamlit as st
import pandas as pd
import numpy as np
from shared_utils import get_connection, quote_table
from ui_utils import render_page_header, render_instructions_block

render_page_header("Search Builder PRO", " Subset any dataset into fantasy-ready tables")

render_instructions_block("""
- Use this page to filter by season, week, position, player, or fantasy stats.
- Save any search subset as a new table for modeling or visualization.
- Fully supports iterative table building.
""")

# Load tables
conn = get_connection()
tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn)
conn.close()

selected_table = st.selectbox("Select table to search", tables["name"].tolist() if not tables.empty else ["No tables found"])

if selected_table != "No tables found":
    conn = get_connection()
    df = pd.read_sql(f"SELECT * FROM {quote_table(selected_table)}", conn)
    conn.close()

    st.write(f"Total rows: {len(df)}")
    st.dataframe(df.head())

    filtered_df = df.copy()

    st.header("Apply Filters")

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

    if "fantasy_points" in df.columns:
        min_fp = float(df["fantasy_points"].min())
        max_fp = float(df["fantasy_points"].max())
        fantasy_range = st.slider("Fantasy Points Range", min_fp, max_fp, (min_fp, max_fp))
        filtered_df = filtered_df[filtered_df["fantasy_points"].between(*fantasy_range)]

    st.write(f"Filtered rows: {len(filtered_df)}")
    st.dataframe(filtered_df)

    new_table_name = st.text_input("Save search result as new table")
    if st.button("💾 Save Search Table"):
        if new_table_name:
            conn = get_connection()
            filtered_df.to_sql(new_table_name, conn, if_exists="replace", index=False)
            conn.close()
            st.success(f"✅ Search result saved as '{new_table_name}'.")
        else:
            st.warning("Please enter a table name to save.")
