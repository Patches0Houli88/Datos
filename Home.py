# Home.py
import streamlit as st

st.set_page_config(page_title="Universal Data Analyzer", layout="wide")
st.title("📊 Universal Data Analyzer")

st.markdown("""
Welcome to your all-in-one data analysis tool!

This app lets you:
- 📂 Upload data (CSV, Excel, JSON, Parquet)
- 🗃️ Store it in a local SQLite database
- 📊 Explore, filter, group, and visualize your data
- 🔍 Profile datasets to understand quality and stats
- 🧠 Write and run SQL queries directly

Use the tabs in the sidebar to switch between analysis modes.

