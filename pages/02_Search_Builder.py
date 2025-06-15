import streamlit as st
import pandas as pd
import numpy as np
from shared_utils import get_connection, quote_table
from ui_utils import render_page_header, render_instructions_block
from filter_utils import apply_universal_filters

render_page_header("Search Builder PRO v4", "🔎 Filter & subset fantasy data with unified controls")

render_instructions_block("""
- Apply filters across Season, Player, and Position.
- Target column aligned to fantasy_points_ppr.
- Subset and save filtered datasets for downstream analysis.
""")

# Load tables
conn = get_connection()
tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn)
conn.close()

selected_table = st.selectbox("Select table to search", tables["name"].tolist() if not tables.empty else ["No tables found"])

if selected_table != "No tables found":
    conn = get_connection()
    df = pd.read_sql(f"SELECT * FROM {quote_table(selected_table)}", conn)
    conn.close()

    st.write(f"Total rows: {len(df)}")
    st.dataframe(df.head())

    st.header("⚙️ Apply Universal Filters")
    filtered_df = apply_universal_filters(df)
    st.dataframe(filtered_df)

    # Optional: add fantasy_points_ppr range slider
    if "fantasy_points_ppr" in filtered_df.columns:
        min_fp = float(filtered_df["fantasy_points_ppr"].min())
        max_fp = float(filtered_df["fantasy_points_ppr"].max())
        fp_range = st.slider("Fantasy PPR Points Range", min_fp, max_fp, (min_fp, max_fp))
        filtered_df = filtered_df[filtered_df["fantasy_points_ppr"].between(*fp_range)]
        st.write(f"Rows after PPR filter: {len(filtered_df)}")

    new_table_name = st.text_input("Save filtered result as new table")
    if st.button("💾 Save Filtered Table"):
        if new_table_name:
            conn = get_connection()
            filtered_df.to_sql(new_table_name, conn, if_exists="replace", index=False)
            conn.close()
            st.success(f"✅ Filtered table saved as '{new_table_name}'")
        else:
            st.warning("Please enter a table name before saving.")
