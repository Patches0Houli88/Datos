# pages/05_DataCleaning.py
import streamlit as st
import pandas as pd
import sqlite3

st.title("🧹 Data Cleaning Tool")
DB_PATH = "universal_data.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cursor.fetchall()]
conn.close()

selected_table = st.selectbox("Select a table to clean", tables if tables else ["No tables available"])

if selected_table != "No tables available":
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(f"SELECT * FROM {selected_table}", conn)
    conn.close()

    st.subheader("🔍 Preview Original Data")
    st.dataframe(df.head())

    with st.expander("🛠️ Missing Values"):
        missing_action = st.selectbox("Choose missing value strategy", ["None", "Drop rows", "Fill with mean", "Fill with median"])
        if missing_action == "Drop rows":
            df = df.dropna()
        elif missing_action == "Fill with mean":
            df = df.fillna(df.mean(numeric_only=True))
        elif missing_action == "Fill with median":
            df = df.fillna(df.median(numeric_only=True))

    with st.expander("📝 Rename Columns"):
        rename_col = st.selectbox("Select a column to rename", df.columns)
        new_col_name = st.text_input("New column name", value=rename_col)
        if st.button("Rename Column"):
            df.rename(columns={rename_col: new_col_name}, inplace=True)
            st.success(f"Renamed `{rename_col}` to `{new_col_name}`")

    with st.expander("🧹 Drop Duplicates"):
        if st.button("Drop duplicate rows"):
            before = len(df)
            df = df.drop_duplicates()
            st.success(f"Dropped {before - len(df)} duplicate rows")

    with st.expander("🔧 Change Data Type"):
        col_to_convert = st.selectbox("Column to convert", df.columns)
        new_type = st.selectbox("New data type", ["int", "float", "str"])
        if st.button("Convert Column Type"):
            try:
                df[col_to_convert] = df[col_to_convert].astype(new_type)
                st.success(f"Converted `{col_to_convert}` to {new_type}")
            except Exception as e:
                st.error(f"Conversion failed: {e}")

    st.subheader("✅ Cleaned Data Preview")
    st.dataframe(df.head())

    save_name = st.text_input("Save cleaned table as", value=f"{selected_table}_cleaned")
    if st.button("💾 Save to SQLite"):
        conn = sqlite3.connect(DB_PATH)
        df.to_sql(save_name, conn, if_exists="replace", index=False)
        conn.close()
        st.success(f"Saved as `{save_name}` in the database!")

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Cleaned Data as CSV", data=csv, file_name=f"{save_name}.csv", mime="text/csv")
