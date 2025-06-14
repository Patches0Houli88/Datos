import streamlit as st
import pandas as pd
from shared_utils import get_connection

st.title("SQL Query Editor")

# Show current tables for user context
st.subheader("Available Tables in Database")
conn = get_connection()
tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn)
st.dataframe(tables)

# SQL Query Box
query = st.text_area("Write your SQL query below:")

# Execute Query
if st.button("Run Query"):
    try:
        df = pd.read_sql(query, conn)
        st.success("✅ Query executed successfully!")
        st.dataframe(df)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download Result CSV", csv, file_name="query_results.csv", mime="text/csv")

    except Exception as e:
        st.error(f"❌ Query failed: {e}")

conn.close()
