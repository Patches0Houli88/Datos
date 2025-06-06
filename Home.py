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

---
🔐 Built by [PatchesOHouli] as an all-in-one tool for data visualization.

---

## 🧭 How To Use This App

### 1. Launching the App
- Visit the Streamlit Cloud URL, or run it locally:
```bash
streamlit run Home.py
```
Make sure your folder has:
- `Home.py`
- A `pages/` directory with features like `01_DataViewer.py`, `06_Predictor.py`, etc.
- A `universal_data.db` file (created automatically once data is saved)

---

### 2. Upload and Explore Data
- Go to **Data Viewer**
- Upload CSV, Excel, JSON, or Parquet
- Preview and save it to the database

💡 Tip: Make sure to include a target column and several features for modeling

---

### 3. Clean Data (Optional)
- Use the **Data Cleaner** tab
- Drop missing values, convert types, remove outliers
- Save the cleaned version back to database

---

### 4. Profile Your Dataset
- Go to **Profile Report**
- View:
  - Column summaries
  - Correlation matrix
  - Null value stats
- Export profile as CSV

---

### 5. Visualize Data
- Go to **Data Explorer**
- Choose filters, groupings, and plot type
- View bar, line, pie, or area charts

---

### 6. Build Prediction Models

#### A. Setup
- Go to **Prediction Engine**
- Select dataset, features, and target

#### B. Configure Model
- Choose `Classification` or `Regression`
- Tune:
  - `n_estimators` (trees)
  - `max_depth` (tree complexity)

#### C. Evaluate
- Compare Random Forest vs Logistic Regression
- Review:
  - Accuracy / RMSE
  - Classification report
  - Confusion matrix
  - Feature importance

#### D. Predict on New Data
- Manually input feature values and run prediction

#### E. Download Results
- Download trained `.pkl` model
- Download prediction results as `.csv`
""")

