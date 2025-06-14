import streamlit as st
import pandas as pd
from shared_utils import get_connection, quote_table

st.title("Profile Report")

conn = get_connection()
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cursor.fetchall()]
conn.close()

selected_table = st.selectbox("Select table to profile", tables if tables else ["No tables found"])

if selected_table != "No tables found":
    conn = get_connection()
    df = pd.read_sql(f"SELECT * FROM {quote_table(selected_table)}", conn)
    conn.close()

    st.write(f"Total rows: {len(df)}")
    st.dataframe(df.head())

    st.subheader("Summary Statistics")
    st.write(df.describe(include="all"))

    st.subheader("Missing Values")
    st.write(df.isnull().sum())

    st.subheader("Column Data Types")
    st.write(df.dtypes)

    csv = df.describe(include="all").to_csv().encode("utf-8")
    st.download_button("Download Summary CSV", csv, file_name=f"{selected_table}_summary.csv", mime="text/csv")
