# pages/06_Predictor.py
import streamlit as st
import pandas as pd
import sqlite3
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import os

st.title("🤖 Prediction Engine")
DB_PATH = "universal_data.db"
MODEL_DIR = "models"
os.makedirs(MODEL_DIR, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cursor.fetchall()]
conn.close()

selected_table = st.selectbox("Select dataset for prediction", tables if tables else ["No tables"])
if selected_table != "No tables":
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(f"SELECT * FROM {selected_table}", conn)
    conn.close()

    st.dataframe(df.head())
    all_cols = df.columns.tolist()

    target = st.selectbox("🎯 Select target column", all_cols)
    features = st.multiselect("🧮 Select feature columns", [col for col in all_cols if col != target])

    if features and target:
        X = df[features].copy()
        y = df[target].copy()

        # Encode categoricals
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

        X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y if y_le else None, test_size=0.2, random_state=42)

        problem_type = st.radio("📌 Problem type", ["Regression", "Classification"])
        min_importance = st.slider("🔎 Drop features below this importance level", 0.0, 1.0, 0.0, 0.01)

        if st.button("🚀 Train Model"):
            if problem_type == "Regression":
                model = RandomForestRegressor()
            else:
                model = RandomForestClassifier(class_weight='balanced')

            model.fit(X_train, y_train)
            preds = model.predict(X_test)

            st.subheader("📊 Feature Importance")
            importances = pd.Series(model.feature_importances_, index=X.columns).sort_values()
            fig, ax = plt.subplots()
            importances.plot(kind="barh", ax=ax)
            ax.set_title("Feature Importance")
            st.pyplot(fig)

            # Auto-drop low-importance features
            selected = importances[importances >= min_importance].index.tolist()
            st.info(f"Using top {len(selected)} features for scoring: {selected}")

            X_train = X_train[selected]
            X_test = X_test[selected]
            model.fit(X_train, y_train)
            preds = model.predict(X_test)

            if problem_type == "Regression":
                st.success(f"Model RMSE: {mean_squared_error(y_test, preds, squared=False):.2f}")
            else:
                st.success(f"Model Accuracy: {accuracy_score(y_test, preds):.2%}")
                st.text("Classification Report")
                st.code(classification_report(y_test, preds))
                st.text("Confusion Matrix")
                fig, ax = plt.subplots()
                sns.heatmap(confusion_matrix(y_test, preds), annot=True, fmt='d', cmap='Blues', ax=ax)
                st.pyplot(fig)

            # Save model
            model_name = f"{selected_table}_{target}_{problem_type.lower()}.pkl"
            joblib.dump((model, selected, label_encoders, y_le), os.path.join(MODEL_DIR, model_name))
            with open(os.path.join(MODEL_DIR, model_name), "rb") as f:
                st.download_button("⬇️ Download Trained Model", f, file_name=model_name)

            # Prediction form
            st.subheader("🔍 Make a Prediction")
            user_input = {}
            for col in selected:
                val = st.text_input(f"Value for {col}")
                user_input[col] = val

            if st.button("Predict on Input"):
                input_df = pd.DataFrame([user_input])
                for col in input_df.columns:
                    if col in label_encoders:
                        input_df[col] = label_encoders[col].transform(input_df[col].astype(str))
                    else:
                        input_df[col] = pd.to_numeric(input_df[col], errors='coerce').fillna(0)

                prediction = model.predict(input_df)
                if y_le:
                    prediction = y_le.inverse_transform([int(prediction[0])])
                st.success(f"📈 Predicted value: {prediction[0]}")
