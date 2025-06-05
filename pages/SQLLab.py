# pages/03_SQLLab.py
import streamlit as st
import pandas as pd
import sqlite3

st.title("🧠 SQL Query Lab")
DB_PATH = "universal_data.db"

conn = sqlite3.connect(DB_PATH)

st.markdown("Write and run SQL queries on your uploaded tables.")
query = st.text_area("Enter your SQL query below:", height=200)

if st.button("Run Query"):
    try:
        result = pd.read_sql(query, conn)
        st.dataframe(result)
        csv = result.to_csv(index=False).encode("utf-8")
        st.download_button("Download Results as CSV", data=csv, file_name="query_results.csv", mime="text/csv")
    except Exception as e:
        st.error(f"❌ Query failed: {e}")

conn.close()