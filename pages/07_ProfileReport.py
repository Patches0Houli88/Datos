import streamlit as st
import pandas as pd
import numpy as np
from shared_utils import get_connection, quote_table
from ui_utils import render_page_header, render_instructions_block

render_page_header("Profile Report PRO", "Quick profiling for datasets")

render_instructions_block("""
- View column types, missing data %, basic stats & uniqueness.
- Helps you quickly audit any dataset before building models.
- Fully compatible with Fantasy filtered tables.
""")

# Load tables
conn = get_connection()
tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn)
conn.close()

selected_table = st.selectbox("Select table to profile", tables["name"].tolist() if not tables.empty else ["No tables found"])

if selected_table != "No tables found":
    conn = get_connection()
    df = pd.read_sql(f"SELECT * FROM {quote_table(selected_table)}", conn)
    conn.close()

    st.write(f"Total rows: {len(df)}")
    st.dataframe(df.head())

    st.header("Column Summary")
    summary = pd.DataFrame({
        "Data Type": df.dtypes,
        "Missing %": df.isnull().mean() * 100,
        "Unique Values": df.nunique(),
    })

    st.dataframe(summary)

    st.header("Descriptive Statistics")
    st.dataframe(df.describe().T)

    st.header("📥 Export Profile Report")
    profile_csv = summary.to_csv(index=True).encode("utf-8")
    st.download_button("Download Profile Summary CSV", profile_csv, file_name="profile_summary.csv")
