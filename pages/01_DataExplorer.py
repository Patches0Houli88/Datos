# DataExplorer.py (Upgraded v2)
import streamlit as st
import pandas as pd
import plotly.express as px
from shared_utils import get_connection, quote_table

st.title("Data Explorer — v2")

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

    st.subheader("Group, Aggregate & Save Subset")

    if len(df.columns) > 0:
        group_col = st.selectbox("Group by column", df.columns)
        numeric_cols = df.select_dtypes(include=["number"]).columns
        if len(numeric_cols) == 0:
            st.warning("No numeric columns available for aggregation.")
        else:
            agg_col = st.selectbox("Aggregate column", numeric_cols)
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

            # Save aggregated result as new table
            new_table_name = st.text_input("Save aggregated result as new table")
            if st.button("💾 Save Aggregated Table"):
                if new_table_name:
                    conn = get_connection()
                    grouped.to_sql(new_table_name, conn, if_exists="replace", index=False)
                    conn.close()
                    st.success(f"✅ Aggregated table saved as '{new_table_name}'.")
                else:
                    st.warning("Please enter a new table name to save.")
