import streamlit as st
import pandas as pd
from shared_utils import get_connection, quote_table
from ui_utils import render_page_header, render_instructions_block

render_page_header("Datos 3.0 PRO", "Full Data Platform — Upload, Explore, Predict")

render_instructions_block("""
- Use this page to upload new datasets or view your current database.
- After upload, data automatically flows to Search, Explorer, Visualizer & Prediction modules.
- Dataset stays fully accessible and reusable throughout the system.
""")

# --- Upload Section ---
st.header("Upload New Dataset")

uploaded_file = st.file_uploader("Upload CSV, Excel, JSON, or Parquet", type=["csv", "xlsx", "json", "parquet"])
table_name = st.text_input("Table Name")

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
            st.success("Preview of uploaded file:")
            st.dataframe(df.head())

            if st.button("💾 Save to Database"):
                conn = get_connection()
                df.to_sql(table_name, conn, if_exists="replace", index=False)
                conn.close()
                st.success(f"✅ Saved table '{table_name}' to database!")

    except Exception as e:
        st.error(f"Upload failed: {e}")

st.divider()

# --- Current Tables Preview ---
st.header("Current Tables In Database")

conn = get_connection()
tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn)
conn.close()

selected_table = st.selectbox("Select table to preview", tables["name"].tolist() if not tables.empty else ["No tables found"])

if selected_table != "No tables found":
    conn = get_connection()
    df = pd.read_sql(f"SELECT * FROM {quote_table(selected_table)} LIMIT 100", conn)
    conn.close()

    st.dataframe(df)
