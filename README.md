# Datos
A professional-grade, multi-page Streamlit app to analyze, visualize, and query structured data.

## Features

-  Upload CSV, Excel, JSON, or Parquet files
-  Load and store in a local SQLite database
-  Explore and filter data
-  Group, aggregate, and visualize with charts
-  Run custom SQL queries
-  Auto profiling via ydata-profiling (pandas-profiling)

## App Pages

1. **Data Viewer** – Upload and load files into SQLite
2. **Visualizer** – Filter, group, and chart your data
3. **SQL Lab** – Write and run SQL queries on any table
4. **Profile Report** – Auto-generate rich profiling reports

## Installation

```bash
pip install -r requirements.txt
```

## ▶ Run the App

```bash
streamlit run Home.py
```

## Deploy on Streamlit Cloud

1. Push the project to GitHub
2. Add `requirements.txt`
3. Go to [streamlit.io/cloud](https://streamlit.io/cloud) → New App
4. Select your repo and set `Home.py` as the main file
5. Click **Deploy**

---

Built by William G. to showcase data analysis and data engineering skills.
