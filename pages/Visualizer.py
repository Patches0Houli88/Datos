# DashboardVisualizer.py — SaaS-Style Visual Analytics
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from shared_utils import get_connection, quote_table

st.set_page_config(page_title="Dashboard Visualizer", layout="wide")
st.title("Dashboard Visualizer")

# Load tables
conn = get_connection()
tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn)
conn.close()

selected_table = st.selectbox("Select dataset for dashboard", tables["name"].tolist() if not tables.empty else ["No tables found"])

if selected_table != "No tables found":
    conn = get_connection()
    df = pd.read_sql(f"SELECT * FROM {quote_table(selected_table)}", conn)
    conn.close()

    st.write(f"Total rows: {len(df)}")
    st.dataframe(df.head())

    st.header("Summary KPIs")
    col1, col2, col3 = st.columns(3)

    numeric_cols = df.select_dtypes(include=["number"]).columns
    if len(numeric_cols) >= 3:
        col1.metric(numeric_cols[0], round(df[numeric_cols[0]].mean(), 2))
        col2.metric(numeric_cols[1], round(df[numeric_cols[1]].sum(), 2))
        col3.metric(numeric_cols[2], df[numeric_cols[2]].nunique())
    elif len(numeric_cols) > 0:
        for i, col in enumerate(numeric_cols):
            st.metric(col, round(df[col].mean(), 2))

    st.header("Build Multiple Charts")
    chart_cols = st.multiselect("Select numeric columns to visualize:", numeric_cols)

    for col in chart_cols:
        st.subheader(f"{col} Distribution")
        fig1 = px.histogram(df, x=col, nbins=30)
        st.plotly_chart(fig1, use_container_width=True)

        fig2 = px.box(df, y=col)
        st.plotly_chart(fig2, use_container_width=True)

    st.header("Category Breakdown")
    category_cols = df.select_dtypes(include="object").columns
    if len(category_cols) > 0:
        cat_col = st.selectbox("Select category column", category_cols)
        cat_summary = df[cat_col].value_counts().reset_index()
        cat_summary.columns = [cat_col, "Count"]
        fig3 = px.pie(cat_summary, names=cat_col, values="Count")
        st.plotly_chart(fig3, use_container_width=True)

    st.header("📅 Time-Series (Optional)")
    datetime_cols = df.select_dtypes(include="datetime").columns
    if len(datetime_cols) > 0:
        time_col = st.selectbox("Select datetime column", datetime_cols)
        ts_summary = df.groupby(time_col).size().reset_index(name="Count")
        fig4 = px.line(ts_summary, x=time_col, y="Count")
        st.plotly_chart(fig4, use_container_width=True)
