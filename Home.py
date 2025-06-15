import streamlit as st
import os
import pandas as pd
import sqlite3
from shared_utils import get_connection

st.set_page_config(page_title="Universal Analyzer 4.0 PRO SaaS", layout="wide")
st.title("Datos 4.0 PRO")

st.markdown("""
Welcome to your fully SaaS-grade, production-ready Fantasy Analytics Engine!

This app includes:

- ✅ Dynamic multi-table ingestion
- ✅ Data Fusion Engine
- ✅ Unified Filter Engine
- ✅ Subset Builder and Aggregator
- ✅ SaaS Dashboards and Visualization
- ✅ Full ML Forecasting Pipelines
- ✅ Cleaner, Profiler, SQL Lab, Model Saver

👉 Use the sidebar navigation to access each module.
""")

# Ensure models directory exists
if not os.path.exists("models"):
    os.makedirs("models")

# 🚀 ✅ CSV Upload Section:
st.header("📂 Upload CSV Data Into SQLite")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("Preview of uploaded data:")
    st.dataframe(df.head())

    table_name = st.text_input("Enter table name to save into database (e.g. player_stats, injuries, weather):")

    if st.button("💾 Save to Database"):
        if table_name:
            conn = get_connection()
            df.to_sql(table_name, conn, if_exists="replace", index=False)
            conn.close()
            st.success(f"✅ Table '{table_name}' saved successfully into SQLite!")
        else:
            st.warning("⚠️ Please enter a table name before saving.")
