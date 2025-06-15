import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os

from shared_utils import get_connection

st.title("🔮 Prediction Playground PRO 4.0")
st.markdown("Upload saved models + future feature data to generate weekly forecasts.")

# Ensure models folder exists
os.makedirs("models", exist_ok=True)

# STEP 1 — MODEL UPLOAD SECTION
st.header("📦 Load Pre-Trained Model")
model_file = st.file_uploader("Upload your saved model file (.pkl)", type=["pkl"])

if model_file:
    loaded_model, feature_cols, target_col = joblib.load(model_file)
    st.success("✅ Model loaded successfully!")
    st.write(f"Model target: `{target_col}`")
    st.write(f"Model features: {feature_cols}")

    # STEP 2 — FEATURE FILE UPLOAD
    st.header("📂 Upload Future Feature Dataset")
    feature_file = st.file_uploader("Upload CSV containing future features", type=["csv"])

    if feature_file:
        future_df = pd.read_csv(feature_file)
        st.write("Preview of uploaded feature data:")
        st.dataframe(future_df.head())

        # Ensure column alignment
        missing_cols = [col for col in feature_cols if col not in future_df.columns]
        if missing_cols:
            st.error(f"❌ Your uploaded file is missing these required columns: {missing_cols}")
        else:
            X_new = future_df[feature_cols].fillna(0)
            preds = loaded_model.predict(X_new)

            future_df["Predicted_" + target_col] = preds
            st.success("✅ Predictions complete!")
            st.dataframe(future_df)

            st.download_button("📥 Download Predictions CSV", future_df.to_csv(index=False), file_name="future_predictions.csv")

# BONUS: Allow quick browsing of locally saved models
st.header("📂 Load Existing Models (from models folder)")
local_models = [f for f in os.listdir("models") if f.endswith(".pkl")]
selected_model = st.selectbox("Select existing local model:", ["None"] + local_models)

if selected_model != "None":
    loaded_model, feature_cols, target_col = joblib.load(os.path.join("models", selected_model))
    st.success(f"✅ Model `{selected_model}` loaded successfully!")
    st.write(f"Target: `{target_col}`")
    st.write(f"Features: {feature_cols}")
