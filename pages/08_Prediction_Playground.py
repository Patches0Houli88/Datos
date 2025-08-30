# pages/08_Prediction_Playground.py  (core changes only)
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os

st.title("🔮 Prediction Playground PRO v4 (Pipeline-Ready)")
st.markdown("Upload raw features; the saved Pipeline handles preprocessing.")

os.makedirs("models", exist_ok=True)

# ===== Step 1: Load pipeline =====
src = st.radio("Choose Model Source:", ["Upload .pkl", "Select from /models"])

meta = None
if src == "Upload .pkl":
    f = st.file_uploader("Upload pipeline (.pkl)", type=["pkl"])
    if f:
        meta = joblib.load(f)
        st.success("✅ Pipeline loaded from upload.")
else:
    local = [f for f in os.listdir("models") if f.endswith(".pkl")]
    name = st.selectbox("Pick a saved model", ["—"] + local)
    if name != "—":
        meta = joblib.load(os.path.join("models", name))
        st.success(f"✅ Loaded models/{name}")

if meta:
    pipe       = meta["pipeline"]
    feat_cols  = meta["feature_cols"]
    target_col = meta["target_col"]

    st.write("Target:", target_col)
    st.write("Expected raw feature columns:", feat_cols)

    # ===== Step 2: Upload future features =====
    csv = st.file_uploader("Upload future features CSV (raw columns)", type=["csv"])
    if csv:
        future_df = pd.read_csv(csv)
        st.write("Preview:")
        st.dataframe(future_df.head())

        missing = [c for c in feat_cols if c not in future_df.columns]
        extra   = [c for c in future_df.columns if c not in feat_cols]

        if missing:
            st.error(f"Missing required columns: {missing}")
        else:
            # Align order; Pipeline will impute/encode/scale internally
            X_new = future_df.reindex(columns=feat_cols)

            # ===== Step 3: Predict =====
            if st.button("Predict"):
                try:
                    preds = pipe.predict(X_new)
                    future_df[f"Predicted_{target_col}"] = preds
                    st.success("✅ Predictions complete!")
                    st.dataframe(future_df.tail(10))
                    st.download_button(
                        "📥 Download Predictions",
                        future_df.to_csv(index=False),
                        file_name="future_predictions.csv"
                    )
                except Exception as e:
                    st.error("Prediction failed.")
                    st.exception(e)
