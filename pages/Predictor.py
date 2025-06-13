# Predictor.py (Patched for Shared Utils)
import streamlit as st
import pandas as pd
from shared_utils import get_connection

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report, confusion_matrix
import joblib
import os
import matplotlib.pyplot as plt
import seaborn as sns

st.title("🤖 Prediction Engine")

MODEL_DIR = "models"
os.makedirs(MODEL_DIR, exist_ok=True)

conn = get_connection()
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cursor.fetchall()]
conn.close()

selected_table = st.selectbox("Select dataset for prediction", tables if tables else ["No tables"])

if selected_table != "No tables":
    conn = get_connection()
    df = pd.read_sql(f"SELECT * FROM {selected_table}", conn)
    conn.close()

    st.dataframe(df.head())
    all_cols = df.columns.tolist()

    target = st.selectbox("🎯 Select target column", all_cols)
    features = st.multiselect("🧮 Select feature columns", [col for col in all_cols if col != target])

    if features and target:
        X = df[features].copy()
        y = df[target].copy()

        label_encoders = {}
        for col in X.select_dtypes(include="object").columns:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))
            label_encoders[col] = le

        if y.dtype == "object":
            y_le = LabelEncoder()
            y = y_le.fit_transform(y.astype(str))
        else:
            y_le = None

        X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y if y_le is not None else None, test_size=0.2, random_state=42)

        problem_type = st.radio("Problem type", ["Classification", "Regression"])

        if problem_type == "Classification":
            rf_model = RandomForestClassifier(class_weight='balanced')
            rf_model.fit(X_train, y_train)
            preds = rf_model.predict(X_test)
            acc = accuracy_score(y_test, preds)

            st.success(f"Model Accuracy: {acc:.2%}")
            st.text("Classification Report")
            st.code(classification_report(y_test, preds))
            st.text("Confusion Matrix")
            fig, ax = plt.subplots()
            sns.heatmap(confusion_matrix(y_test, preds), annot=True, fmt='d', cmap='Blues', ax=ax)
            st.pyplot(fig)

            model_name = f"{selected_table}_{target}_classifier.pkl"
            joblib.dump((rf_model, features, label_encoders, y_le), os.path.join(MODEL_DIR, model_name))
            with open(os.path.join(MODEL_DIR, model_name), "rb") as f:
                st.download_button("⬇️ Download Trained Model", f, file_name=model_name)

        elif problem_type == "Regression":
            model = RandomForestRegressor()
            model.fit(X_train, y_train)
            preds = model.predict(X_test)

            rmse = mean_squared_error(y_test, preds, squared=False)
            st.success(f"📉 RMSE: {rmse:.2f}")

            model_name = f"{selected_table}_{target}_regressor.pkl"
            joblib.dump((model, features, label_encoders, y_le), os.path.join(MODEL_DIR, model_name))
            with open(os.path.join(MODEL_DIR, model_name), "rb") as f:
                st.download_button("⬇️ Download Trained Model", f, file_name=model_name)
