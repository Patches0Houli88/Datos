import streamlit as st
import pandas as pd
import numpy as np
from shared_utils import get_connection, quote_table
from ui_utils import render_page_header, render_instructions_block

render_page_header("Data Cleaner PRO", "🧹 Simplify your datasets before modeling")

render_instructions_block("""
- Drop missing rows entirely if desired.
- Detect & remove outliers automatically (z-score based).
- Save cleaned versions for modeling & visualization.
""")

# Load tables
conn = get_connection()
tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn)
conn.close()

selected_table = st.selectbox("Select table to clean", tables["name"].tolist() if not tables.empty else ["No tables found"])

if selected_table != "No tables found":
    conn = get_connection()
    df = pd.read_sql(f"SELECT * FROM {quote_table(selected_table)}", conn)
    conn.close()

    st.write(f"Total rows: {len(df)}")
    st.dataframe(df.head())

    df_clean = df.copy()

    st.header("Cleaning Options")
    drop_na = st.checkbox("Drop rows with missing values?")
    remove_outliers = st.checkbox("Remove numeric outliers? (Z-score > 3)")

    if drop_na:
        df_clean = df_clean.dropna()

    if remove_outliers:
        numeric_cols = df_clean.select_dtypes(include=["number"]).columns
        for col in numeric_cols:
            z_scores = np.abs((df_clean[col] - df_clean[col].mean()) / df_clean[col].std())
            df_clean = df_clean[z_scores < 3]

    st.write(f"Remaining rows after cleaning: {len(df_clean)}")
    st.dataframe(df_clean)

    new_table_name = st.text_input("Save cleaned table as:")
    if st.button("💾 Save Cleaned Table"):
        if new_table_name:
            conn = get_connection()
            df_clean.to_sql(new_table_name, conn, if_exists="replace", index=False)
            conn.close()
            st.success(f"✅ Cleaned table saved as '{new_table_name}'")
        else:
            st.warning("Enter table name before saving.")
