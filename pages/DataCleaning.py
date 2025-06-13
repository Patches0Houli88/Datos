# DataCleaner.py (Patched for Shared Utils)
import streamlit as st
import pandas as pd
from shared_utils import get_connection

st.title("🧼 Data Cleaner")

conn = get_connection()
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cursor.fetchall()]
conn.close()

selected_table = st.selectbox("Select table to clean", tables if tables else ["No tables found"])

if selected_table != "No tables found":
    conn = get_connection()
    df = pd.read_sql(f"SELECT * FROM {selected_table}", conn)
    conn.close()

    st.write(f"Total rows: {len(df)}")
    st.dataframe(df.head())

    st.subheader("Cleaning Options")

    if st.checkbox("Drop rows with missing values"):
        df.dropna(inplace=True)

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if numeric_cols:
        st.write("Numeric columns: ", numeric_cols)
        for col in numeric_cols:
            outlier_thresh = st.slider(f"Remove outliers in {col}", 0.0, 5.0, 3.0, 0.5)
            zscore = (df[col] - df[col].mean()) / df[col].std()
            df = df[abs(zscore) < outlier_thresh]

    st.write(f"Cleaned data shape: {df.shape}")
    st.dataframe(df)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download Cleaned CSV", csv, file_name=f"{selected_table}_cleaned.csv", mime="text/csv")

    if st.button("Save Cleaned Table"):
        conn = get_connection()
        new_table = selected_table + "_cleaned"
        df.to_sql(new_table, conn, if_exists="replace", index=False)
        conn.close()
        st.success(f"Saved cleaned table as '{new_table}' in database.")
