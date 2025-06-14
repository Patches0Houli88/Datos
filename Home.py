# Home.py — Enhanced with Explore & SQL Lab shortcuts after save

import streamlit as st
import pandas as pd
import sqlite3
from shared_utils import get_connection, quote_table

st.set_page_config(page_title="Universal Data Analyzer", layout="wide")
st.title("📊 Universal Data Analyzer — Home Dashboard")

# --- Universal Data Import Section (still intact)
st.header("📂 Import Your Own Dataset")

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

                # Show quick links after successful save
                st.markdown("---")
                st.subheader("Next Actions")
                st.markdown("[🔎 Explore This Table](#/pages/04_DataExplorer)", unsafe_allow_html=True)
                st.markdown("[🧮 Open SQL Lab](#/pages/05_SQLQueryEditor)", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Upload failed: {e}")

st.divider()

# --- Live Table Preview with Subset Filter Builder ---
st.header("🧮 Current Tables & Interactive Subset Builder")

conn = get_connection()
tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn)
conn.close()

selected_table = st.selectbox("Select table to preview & filter", tables["name"].tolist() if not tables.empty else ["No tables found"])

if selected_table != "No tables found":
    conn = get_connection()
    df = pd.read_sql(f"SELECT * FROM {quote_table(selected_table)}", conn)
    conn.close()

    st.subheader("Live Table Preview")
    st.dataframe(df.head())

    st.subheader("Optional: Apply Filters")

    filter_column = st.selectbox("Filter column", df.columns)
    filter_value = st.text_input("Contains text (leave blank for no filter)")

    filtered_df = df.copy()
    if filter_value:
        filtered_df = df[df[filter_column].astype(str).str.contains(filter_value, case=False, na=False)]

    st.write(f"Filtered rows: {len(filtered_df)}")
    st.dataframe(filtered_df)

    # Save filtered subset as new table
    new_table_name = st.text_input("Save filtered result as new table")
    if st.button("💾 Save Filtered Table"):
        if new_table_name:
            conn = get_connection()
            filtered_df.to_sql(new_table_name, conn, if_exists="replace", index=False)
            conn.close()
            st.success(f"✅ Filtered subset saved as '{new_table_name}'.")
        else:
            st.warning("Please enter a new table name to save.")

st.divider()

# --- Live Table Inventory ---
st.header("📊 Current Tables In Database")
conn = get_connection()
tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn)
conn.close()
st.dataframe(tables)
