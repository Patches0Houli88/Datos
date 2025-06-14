import streamlit as st
import pandas as pd
import plotly.express as px
from shared_utils import get_connection, quote_table

st.title("Data Explorer")

conn = get_connection()
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cursor.fetchall()]
conn.close()

selected_table = st.selectbox("Select table to explore", tables if tables else ["No tables found"])

if selected_table != "No tables found":
    conn = get_connection()
    df = pd.read_sql(f"SELECT * FROM {quote_table(selected_table)}", conn)
    conn.close()

    st.write(f"Total rows: {len(df)}")
    st.dataframe(df.head())

    st.subheader("Group & Aggregate")

    group_col = st.selectbox("Group by column", df.columns)
    agg_col = st.selectbox("Aggregate column", df.select_dtypes(include=["number"]).columns)

    agg_func = st.selectbox("Aggregation Function", ["sum", "mean", "max", "min", "count"])

    grouped = df.groupby(group_col)[agg_col].agg(agg_func).reset_index()
    st.write(grouped)

    chart_type = st.selectbox("Chart Type", ["Bar", "Line", "Pie"])

    if chart_type == "Bar":
        fig = px.bar(grouped, x=group_col, y=agg_col)
    elif chart_type == "Line":
        fig = px.line(grouped, x=group_col, y=agg_col)
    else:
        fig = px.pie(grouped, names=group_col, values=agg_col)

    st.plotly_chart(fig, use_container_width=True)
