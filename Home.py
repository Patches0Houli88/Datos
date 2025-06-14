# Home.py (Patched: Add Universal Importer Inline)
import streamlit as st
import pandas as pd
import sqlite3
import os
from shared_utils import get_connection

st.set_page_config(page_title="Universal Data Analyzer", layout="wide")
st.title("Universal Data Analyzer — Home")

# --- Universal Data Import Section ---
st.header("Import Your Own Dataset")

uploaded_file = st.file_uploader("Upload CSV, Excel, JSON, or Parquet", type=["csv", "xlsx", "json", "parquet"])
table_name = st.text_input("Enter table name to save in database")

if uploaded_file and table_name:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)
        elif uploaded_file.name.endswith(".json"):
            df = pd.read_json(uploaded_file)
        elif uploaded_file.name.endswith(".parquet"):
            df = pd.read_parquet(uploaded_file)
        else:
            st.error("Unsupported file type.")
            df = None

        if df is not None:
            st.dataframe(df.head())
            if st.button("💾 Save to SQLite"):
                conn = get_connection()
                df.to_sql(table_name, conn, if_exists="replace", index=False)
                conn.close()
                st.success(f"✅ Saved table '{table_name}' to database.")

    except Exception as e:
        st.error(f"Upload failed: {e}")

st.divider()

# --- Current Tables Preview ---
st.header("Current Tables in Database")
conn = get_connection()
tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn)
conn.close()
st.dataframe(tables)
