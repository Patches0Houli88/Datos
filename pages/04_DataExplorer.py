import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from shared_utils import get_connection, quote_table
from ui_utils import render_page_header, render_instructions_block
from filter_utils import apply_universal_filters

render_page_header("Data Explorer PRO v3", "Explore, aggregate & visualize fantasy datasets")

render_instructions_block("""
- Apply player/season/position filters first.
- Group & aggregate on any field.
- Visualize results and optionally save grouped tables.
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

    st.header("🔎 Apply Universal Filters")
    df_filtered = apply_universal_filters(df)
    st.dataframe(df_filtered)

    st.header("📊 Group & Aggregate")
    group_cols = [col for col in df_filtered.columns if df_filtered[col].nunique() < 100]

    if group_cols:
        group_col = st.selectbox("Group by column", group_cols)
        numeric_cols = df_filtered.select_dtypes(include=["number"]).columns.tolist()

        # Default to fantasy_points_ppr
        if "fantasy_points_ppr" in numeric_cols:
            default_idx = numeric_cols.index("fantasy_points_ppr")
        else:
            default_idx = 0

        agg_col = st.selectbox("Aggregate numeric column", numeric_cols, index=default_idx)
        agg_func = st.selectbox("Aggregation function", ["sum", "mean", "max", "min", "count"])

        grouped = df_filtered.groupby(group_col)[agg_col].agg(agg_func).reset_index()
        st.write(grouped)

        st.header("📈 Chart Builder")
        chart_type = st.selectbox("Chart Type", ["Bar", "Line", "Pie"])
        if chart_type == "Bar":
            fig = px.bar(grouped, x=group_col, y=agg_col)
        elif chart_type == "Line":
            fig = px.line(grouped, x=group_col, y=agg_col)
        else:
            fig = px.pie(grouped, names=group_col, values=agg_col)

        st.plotly_chart(fig, use_container_width=True)

        new_table_name = st.text_input("Save Aggregated Table")
        if st.button("💾 Save Aggregated Table"):
            if new_table_name:
                conn = get_connection()
                grouped.to_sql(new_table_name, conn, if_exists="replace", index=False)
                conn.close()
                st.success(f"✅ Saved aggregated table '{new_table_name}'.")
            else:
                st.warning("Please enter a table name to save.")
