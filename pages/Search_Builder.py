# Universal Search Builder v1 (Full Search Layer)
import streamlit as st
import pandas as pd
import numpy as np
from shared_utils import get_connection, quote_table

st.title("Search Builder")

# Load tables from DB
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

    st.header("Build Search Filters")

    filtered_df = df.copy()
    filter_cols = st.multiselect("Select columns to apply search filters:", df.columns)

    for col in filter_cols:
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
            else:
                filtered_df = filtered_df[df[col].astype(str).str.len() > 0]

    st.write(f"Filtered rows: {len(filtered_df)}")
    st.dataframe(filtered_df)

    # Save filtered result
    new_table_name = st.text_input("Save search result as new table")
    if st.button("💾 Save Search Table"):
        if new_table_name:
            conn = get_connection()
            filtered_df.to_sql(new_table_name, conn, if_exists="replace", index=False)
            conn.close()
            st.success(f"✅ Search result saved as '{new_table_name}'.")
        else:
            st.warning("Please enter a new table name to save.")
