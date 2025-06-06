# Home.py
import streamlit as st

st.set_page_config(page_title="Universal Data Analyzer", layout="wide")
st.title("Universal Data Analyzer")

st.markdown("""
Welcome to your all-in-one data analysis tool!

This app lets you:
- 📂 Upload data (CSV, Excel, JSON, Parquet)
- 🗃️ Store it in a local SQLite database
- 📊 Explore, filter, group, and visualize your data
- 🔍 Profile datasets to understand quality and stats
- 🧠 Write and run SQL queries directly

Use the tabs in the sidebar to switch between analysis modes.

---
🔐 Built by [PatchesOHouli] as an all-in-one tool for data visualization.
""")

with st.sidebar.expander("How To Use This App"):
    st.markdown("""
### 1. Launch
- Run `streamlit run Home.py` locally or use Streamlit Cloud

### 2. Upload
- Upload CSV, Excel, JSON, or Parquet via **Data Viewer**
- Save data to SQLite database

### 3. Clean
- Use **Data Cleaner** tab to fix missing values, types, etc.

### 4. Profile
- View summary stats and correlation in **Profile Report**

### 5. Explore
- Filter, group, and chart using **Data Explorer**

### 6. Predict
- Use **Prediction Engine**:
  - Select features + target
  - Tune model (trees/depth)
  - Compare RF vs Logistic
  - Predict and download results
    """)

