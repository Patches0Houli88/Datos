# Universal Data Generator v2.1 (Stateful with Shared Utils)
import streamlit as st
import pandas as pd
import numpy as np
import random
from faker import Faker
from shared_utils import get_connection

fake = Faker()

st.title("🛠 Universal Data Generator v2.1 (Stateful Version)")

# Initialize session state for dataframe
if "generated_df" not in st.session_state:
    st.session_state["generated_df"] = None

# Function to map type + generator to actual data
def generate_column_data(data_type, generator, n_rows):
    if data_type == "string":
        if generator == "name":
            return [fake.name() for _ in range(n_rows)]
        elif generator == "email":
            return [fake.email() for _ in range(n_rows)]
        elif generator == "city":
            return [fake.city() for _ in range(n_rows)]
        elif generator == "company":
            return [fake.company() for _ in range(n_rows)]
        elif generator == "job":
            return [fake.job() for _ in range(n_rows)]
        else:
            return [fake.word() for _ in range(n_rows)]
    elif data_type == "int":
        return [random.randint(1000, 9999) for _ in range(n_rows)]
    elif data_type == "float":
        return [round(random.uniform(1000, 9999), 2) for _ in range(n_rows)]
    elif data_type == "date":
        return [fake.date_between(start_date='-3y', end_date='today') for _ in range(n_rows)]
    elif data_type == "bool":
        return [random.choice([True, False]) for _ in range(n_rows)]
    elif data_type == "category":
        return ["category_placeholder"] * n_rows
    else:
        return [""] * n_rows

# STEP 1 — Column Definitions
st.header("📋 Define Your Schema")

n_rows = st.number_input("Number of Rows", 100, 10000, 100)
n_cols = st.number_input("Number of Columns", 1, 20, 3)

schema = []
for i in range(n_cols):
    st.subheader(f"Column {i+1}")
    col_name = st.text_input(f"Column {i+1} Name", key=f"name_{i}")
    data_type = st.selectbox("Data Type", ["string", "int", "float", "date", "bool", "category"], key=f"type_{i}")

    generator = None
    if data_type == "string":
        generator = st.selectbox("Optional Content Generator", ["name", "email", "city", "company", "job", "word"], key=f"gen_{i}")

    schema.append({
        "name": col_name,
        "type": data_type,
        "generator": generator
    })

# STEP 2 — Generate Button
if st.button("🚀 Generate Data"):
    df_data = {}
    for col in schema:
        col_name = col["name"]
        col_type = col["type"]
        generator = col.get("generator")
        df_data[col_name] = generate_column_data(col_type, generator, n_rows)

    df = pd.DataFrame(df_data)
    st.session_state["generated_df"] = df  # Store in session state

    st.success("✅ Dataset Generated!")
    st.dataframe(df)

# If dataset exists in state, show export/save options
if st.session_state["generated_df"] is not None:
    df = st.session_state["generated_df"]
    st.subheader("⬇️ Export or Save Generated Data")

    # CSV Export
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, file_name="generated_data.csv", mime="text/csv")

    # Save directly to SQLite using shared utils
    db_table_name = st.text_input("Enter SQLite Table Name to Save")

    if st.button("💾 Save to SQLite Database"):
        conn = get_connection()
        df.to_sql(db_table_name, conn, if_exists="replace", index=False)
        conn.close()
        st.success(f"✅ Saved as '{db_table_name}' in database successfully")
