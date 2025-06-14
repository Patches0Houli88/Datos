# DataExplorer.py — Fully Unified v3 with Filters + Aggregation + Save
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from shared_utils import get_connection, quote_table

st.title("Data Explorer — v3 Full Workflow")

# Load tables from DB
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
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            min_val, max_val = st.slider(f"{col} range", float(df[col].min()), float(df[col].max()), (float(df[col].min()), float(df[col].max())))
            filtered_df = filtered_df[(filtered_df[col] >= min_val) & (filtered_df[col] <= max_val)]
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            date_min = pd.to_datetime(df[col].min())
            date_max = pd.to_datetime(df[col].max())
            date_range = st.date_input(f"{col} date range", (date_min, date_max))
            filtered_df = filtered_df[(df[col] >= pd.to_datetime(date_range[0])) & (df[col] <= pd.to_datetime(date_range[1]))]
        elif df[col].nunique() <= 25:
            selected_values = st.multiselect(f"{col} values", options=df[col].unique(), default=list(df[col].unique()))
            filtered_df = filtered_df[filtered_df[col].isin(selected_values)]
        else:
            substring = st.text_input(f"{col} contains")
            if substring:
                filtered_df = filtered_df[filtered_df[col].astype(str).str.contains(substring, case=False, na=False)]

    st.write(f"Filtered rows: {len(filtered_df)}")
    st.dataframe(filtered_df)

    st.header("Group, Aggregate & Visualize")

    if len(filtered_df.columns) > 0:
        group_col = st.selectbox("Group by column", filtered_df.columns)
        numeric_cols = filtered_df.select_dtypes(include=["number"]).columns
        if len(numeric_cols) == 0:
            st.warning("No numeric columns available for aggregation.")
        else:
            agg_col = st.selectbox("Aggregate column", numeric_cols)
            agg_func = st.selectbox("Aggregation Function", ["sum", "mean", "max", "min", "count"])

            grouped = filtered_df.groupby(group_col)[agg_col].agg(agg_func).reset_index()
            st.write(grouped)

            chart_type = st.selectbox("Chart Type", ["Bar", "Line", "Pie"])

            if chart_type == "Bar":
                fig = px.bar(grouped, x=group_col, y=agg_col)
            elif chart_type == "Line":
                fig = px.line(grouped, x=group_col, y=agg_col)
            else:
                fig = px.pie(grouped, names=group_col, values=agg_col)

            st.plotly_chart(fig, use_container_width=True)

            new_table_name = st.text_input("Save aggregated result as new table")
            if st.button("💾 Save Aggregated Table"):
                if new_table_name:
                    conn = get_connection()
                    grouped.to_sql(new_table_name, conn, if_exists="replace", index=False)
                    conn.close()
                    st.success(f"✅ Aggregated table saved as '{new_table_name}'.")
                else:
                    st.warning("Please enter a new table name to save.")
