# pages/04_ProfileReport.py
import streamlit as st
import pandas as pd
import sqlite3

st.title("🔎 Data Profile Report")
DB_PATH = "universal_data.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cursor.fetchall()]
conn.close()

selected_table = st.selectbox("Select a table for profiling", tables if tables else ["No tables"])

if selected_table != "No tables":
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(f"SELECT * FROM {selected_table}", conn)
    conn.close()

    st.write(f"Generating report for `{selected_table}`...")

    try:
        from ydata_profiling import ProfileReport
        from streamlit_pandas_profiling import st_profile_report

        profile = ProfileReport(df, title="Data Profiling Report", explorative=True)
        st_profile_report(profile)

    except Exception as e:
        st.error("⚠️ Failed to generate profile report.")
        st.exception(e)
