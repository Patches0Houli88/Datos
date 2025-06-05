# pages/04_ProfileReport.py
import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import io

st.title("🧪 Lightweight Data Profiler")
DB_PATH = "universal_data.db"

# Connect and list tables
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cursor.fetchall()]
conn.close()

selected_table = st.selectbox("Choose a table to profile", tables if tables else ["No tables"])

if selected_table != "No tables":
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(f"SELECT * FROM {selected_table}", conn)
    conn.close()

    st.subheader("🧮 Summary Statistics")
    stats = df.describe(include='all').transpose()
    st.dataframe(stats)

    # Export summary stats
    csv = stats.to_csv().encode("utf-8")
    st.download_button("⬇️ Download Summary as CSV", csv, file_name=f"{selected_table}_summary.csv", mime="text/csv")

    st.subheader("📌 Missing Values")
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    if not missing.empty:
        st.write(missing)
        missing_csv = missing.to_csv().encode("utf-8")
        st.download_button("⬇️ Download Missing Values", missing_csv, file_name=f"{selected_table}_missing.csv", mime="text/csv")
    else:
        st.write("✅ No missing values found.")

    st.subheader("📊 Column Distributions")
    num_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    cat_cols = df.select_dtypes(include=['object']).columns.tolist()

    if num_cols:
        col_to_plot = st.selectbox("Pick a numeric column for histogram", num_cols)
        fig = px.histogram(df, x=col_to_plot)
        st.plotly_chart(fig)

    st.subheader("📈 Correlation Heatmap")
    if len(num_cols) >= 2:
        corr = df[num_cols].corr()
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
        st.pyplot(fig)

        # Export heatmap data
        corr_csv = corr.to_csv().encode("utf-8")
        st.download_button("⬇️ Download Correlation Matrix", corr_csv, file_name=f"{selected_table}_correlations.csv", mime="text/csv")
    else:
        st.info("Not enough numeric columns to show correlation heatmap.")
