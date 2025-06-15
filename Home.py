import streamlit as st
import os

st.set_page_config(page_title="Datos 4.0 PRO SaaS", layout="wide")

st.title("Datos 4.0 PRO")

st.markdown("""
Welcome to your fully SaaS-grade, production-ready Fantasy Analytics Engine!

This app includes:

- ✅ Dynamic multi-table ingestion
- ✅ Data Fusion Engine
- ✅ Unified Filter Engine
- ✅ Subset Builder and Aggregator
- ✅ SaaS Dashboards and Visualization
- ✅ Full ML Forecasting Pipelines
- ✅ Cleaner, Profiler, SQL Lab, Model Saver

👉 Use the sidebar navigation to access each module.
""")

# Ensure models directory exists for ML model saving
if not os.path.exists("models"):
    os.makedirs("models")
