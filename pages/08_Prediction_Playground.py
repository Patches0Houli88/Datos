import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os

from shared_utils import get_connection

st.title("🔮 Prediction Playground PRO v4 (SaaS Upgrade)")
st.markdown("**Guided 3-Step Forecasting System**")

# Ensure models folder exists
os.makedirs("models", exist_ok=True)

# STEP 1 — MODEL SELECTION (UPLOAD OR LOAD)
st.header("Step 1️⃣ — Load Trained Model")

model_option = st.radio("Choose Model Source:", ["Upload Model (.pkl)", "Select Existing Saved Model"])

loaded_model = None
feature_cols = []
target_col = None

if model_option == "Upload Model (.pkl)":
    model_file = st.file_uploader("Upload your model (.pkl)", type=["pkl"])
    if model_file:
        loaded_model, feature_cols, target_col = joblib.load(model_file)
        st.success("✅ Model uploaded successfully!")
elif model_option == "Select Existing Saved Model":
    local_models = [f for f in os.listdir("models") if f.endswith(".pkl")]
    selected_model = st.selectbox("Select saved model", ["None"] + local_models)
    if selected_model != "None":
        loaded_model, feature_cols, target_col = joblib.load(os.path.join("models", selected_model))
        st.success(f"✅ Model `{selected_model}` loaded successfully!")

# Only show Step 2 if model loaded successfully
if loaded_model:
    st.write(f"Model target: `{target_col}`")
    st.write(f"Model features: {feature_cols}")

    # STEP 2 — FUTURE FEATURES UPLOAD
    st.header("Step 2️⃣ — Upload Future Feature Dataset")
    st.markdown("👉 **IMPORTANT:** Use your pre-built template CSV matching model features.")

    feature_file = st.file_uploader("Upload CSV containing future features", type=["csv"])

    if feature_file:
        future_df = pd.read_csv(feature_file)
        st.write("Preview of future feature data:")
        st.dataframe(future_df.head())

        missing_cols = [col for col in feature_cols if col not in future_df.columns]
        if missing_cols:
            st.error(f"❌ Your uploaded file is missing required columns: {missing_cols}")
        else:
            # STEP 3 — PREDICTIONS
            st.header("Step 3️⃣ — Generate Predictions")
            if st.button("Predict Future Outcomes"):
                X_new = future_df[feature_cols].fillna(0)
                preds = loaded_model.predict(X_new)

                future_df["Predicted_" + target_col] = preds
                st.success("✅ Predictions complete!")
                st.dataframe(future_df)

                st.download_button("📥 Download Predictions CSV", future_df.to_csv(index=False), file_name="future_predictions.csv")
