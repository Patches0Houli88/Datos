# DataViewer.py (Patched for Shared Utils + RowID-Safe)
import streamlit as st
import pandas as pd
from shared_utils import get_connection

st.title("Data Viewer")

conn = get_connection()
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cursor.fetchall()]
conn.close()

selected_table = st.selectbox("Select table to view", tables if tables else ["No tables found"])

if selected_table != "No tables found":
    conn = get_connection()
    df = pd.read_sql(f"SELECT * FROM {selected_table}", conn)
    conn.close()

    st.write(f"Total rows: {len(df)}")

    # Safe handling of rowid column
    filterable_columns = df.columns.drop("rowid") if "rowid" in df.columns else df.columns
    filter_col = st.selectbox("Filter by column", filterable_columns)
    filter_val = st.text_input("Contains (optional)")
    if filter_val:
        df = df[df[filter_col].astype(str).str.contains(filter_val, na=False, case=False)]

    st.dataframe(df)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, file_name=f"{selected_table}.csv", mime="text/csv")
