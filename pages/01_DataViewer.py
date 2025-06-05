# pages/01_DataViewer.py
import streamlit as st
import pandas as pd
import sqlite3

st.title("📂 Data Viewer & Loader")
DB_PATH = "universal_data.db"

uploaded_file = st.file_uploader("Upload a data file (CSV, Excel, JSON, Parquet)", type=["csv", "xlsx", "xls", "json", "parquet"])

if uploaded_file:
    file_type = uploaded_file.name.split('.')[-1]
    if file_type in ["xlsx", "xls"]:
        df = pd.read_excel(uploaded_file)
    elif file_type == "json":
        df = pd.read_json(uploaded_file)
    elif file_type == "parquet":
        df = pd.read_parquet(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file)

    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    st.dataframe(df.head())
    table_name = st.text_input("Enter table name to save in DB", value="my_table")
    if st.button("📥 Load into SQLite DB"):
        conn = sqlite3.connect(DB_PATH)
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        conn.close()
        st.success(f"Loaded into `{table_name}` ✅")
