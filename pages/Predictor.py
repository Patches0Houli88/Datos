import streamlit as st
import pandas as pd
import os
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

from shared_utils import get_connection, quote_table
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report, confusion_matrix
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression

st.title("🔍 Advanced Prediction Engine")

MODEL_DIR = "models"
os.makedirs(MODEL_DIR, exist_ok=True)

# Load table list using shared utils
conn = get_connection()
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cursor.fetchall()]
conn.close()

selected_table = st.selectbox("Select dataset", tables if tables else ["No tables"])
if selected_table != "No tables":
    conn = get_connection()
    df = pd.read_sql(f"SELECT * FROM {quote_table(selected_table)}", conn)
    conn.close()

    st.dataframe(df.head())
    all_cols = df.columns.tolist()

    target = st.selectbox("🎯 Select target column", all_cols)
    features = st.multiselect("🧮 Select features", [col for col in all_cols if col != target])

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
            st.subheader("🛠️ Tuning Parameters")
            n_estimators = st.slider("n_estimators", 10, 300, 100, 10)
            max_depth = st.slider("max_depth", 1, 20, 5, 1)

            if st.button("🚀 Train and Compare Models"):
                rf_model = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, class_weight='balanced')
                log_model = LogisticRegression(max_iter=1000)

                rf_model.fit(X_train, y_train)
                log_model.fit(X_train, y_train)

                rf_preds = rf_model.predict(X_test)
                log_preds = log_model.predict(X_test)

                rf_acc = accuracy_score(y_test, rf_preds)
                log_acc = accuracy_score(y_test, log_preds)

                st.success(f"🌲 Random Forest Accuracy: {rf_acc:.2%}")
                st.success(f"📈 Logistic Regression Accuracy: {log_acc:.2%}")

                best_model = rf_model if rf_acc >= log_acc else log_model
                model_name = f"{selected_table}_{target}_best_classifier.pkl"
                joblib.dump((best_model, features, label_encoders, y_le), os.path.join(MODEL_DIR, model_name))

                # Classification report and confusion matrix
                st.subheader("📋 Classification Report")
                st.code(classification_report(y_test, rf_preds if best_model==rf_model else log_preds))
                st.subheader("🔲 Confusion Matrix")
                fig, ax = plt.subplots()
                sns.heatmap(confusion_matrix(y_test, rf_preds if best_model==rf_model else log_preds), annot=True, fmt='d', cmap='Blues', ax=ax)
                st.pyplot(fig)

                pred_df = X_test.copy()
                pred_df["Actual"] = y_test
                pred_df["Predicted"] = rf_preds if best_model==rf_model else log_preds
                st.download_button("⬇️ Download Predictions CSV", pred_df.to_csv(index=False), file_name="predictions.csv")

        elif problem_type == "Regression":
            model = RandomForestRegressor()
            model.fit(X_train, y_train)
            preds = model.predict(X_test)

            rmse = mean_squared_error(y_test, preds, squared=False)
            st.success(f"📉 RMSE: {rmse:.2f}")

            model_name = f"{selected_table}_{target}_regressor.pkl"
            joblib.dump((model, features, label_encoders, y_le), os.path.join(MODEL_DIR, model_name))

            pred_df = X_test.copy()
            pred_df["Actual"] = y_test
            pred_df["Predicted"] = preds
            st.download_button("⬇️ Download Predictions CSV", pred_df.to_csv(index=False), file_name="regression_predictions.csv")

        st.markdown("---")
        st.subheader("🔮 Predict on New Input")
        user_input = {col: st.text_input(f"Input for {col}") for col in features}
        if st.button("Predict"):
            input_df = pd.DataFrame([user_input])
            for col in input_df.columns:
                if col in label_encoders:
                    input_df[col] = label_encoders[col].transform(input_df[col].astype(str))
                else:
                    input_df[col] = pd.to_numeric(input_df[col], errors='coerce').fillna(0)

            model = joblib.load(os.path.join(MODEL_DIR, model_name))
            model, selected_features, encoders, y_le = model
            input_df = input_df[selected_features]
            prediction = model.predict(input_df)
            if y_le:
                prediction = y_le.inverse_transform([int(prediction[0])])
            st.success(f"Predicted value: {prediction[0]}")
