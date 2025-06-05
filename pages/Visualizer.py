# pages/02_Visualizer.py
import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

st.title("📊 Data Visualizer")
DB_PATH = "universal_data.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cursor.fetchall()]

selected_table = st.selectbox("Choose a table to visualize", tables if tables else ["No tables available"])

if selected_table and selected_table != "No tables available":
    df = pd.read_sql(f"SELECT * FROM {selected_table}", conn)
    cols = df.columns.tolist()
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()

    st.markdown("### 🔍 Filter and Group")
    filter_column = st.selectbox("Filter by column", options=cols)
    if pd.api.types.is_numeric_dtype(df[filter_column]):
        min_val, max_val = st.slider("Value range", float(df[filter_column].min()), float(df[filter_column].max()), (float(df[filter_column].min()), float(df[filter_column].max())))
        filtered_df = df[df[filter_column].between(min_val, max_val)]
    else:
        unique_vals = df[filter_column].dropna().unique().tolist()
        selected_vals = st.multiselect("Select values", unique_vals, default=unique_vals)
        filtered_df = df[df[filter_column].isin(selected_vals)]

    st.markdown("### 🧮 Group and Visualize")
    group_col = st.selectbox("Group by column", options=cols)
    agg_col = st.selectbox("Aggregate column", options=numeric_cols)
    agg_func = st.selectbox("Aggregation function", ["sum", "mean", "count", "max", "min"])

    grouped = filtered_df.groupby(group_col, as_index=False)[agg_col].agg(agg_func)
    chart_type = st.selectbox("Chart Type", ["Bar", "Line", "Area", "Pie"])

    if chart_type == "Bar":
        st.bar_chart(grouped.set_index(group_col))
    elif chart_type == "Line":
        st.line_chart(grouped.set_index(group_col))
    elif chart_type == "Area":
        st.area_chart(grouped.set_index(group_col))
    elif chart_type == "Pie":
        fig = px.pie(grouped, names=group_col, values=agg_col)
        st.plotly_chart(fig)

    st.markdown("### 📈 Distribution & Correlation")
    selected_col = st.selectbox("Column for Histogram", numeric_cols)
    fig = px.histogram(filtered_df, x=selected_col, nbins=30)
    st.plotly_chart(fig)

    if len(numeric_cols) >= 2:
        st.markdown("### 📊 Correlation Heatmap")
        corr = filtered_df[numeric_cols].corr()
        fig, ax = plt.subplots()
        sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
        st.pyplot(fig)

conn.close()