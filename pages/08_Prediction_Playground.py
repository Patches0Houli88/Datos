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

    # Determine expected features
    expected = None
    if hasattr(loaded_model, "feature_names_in_"):
        expected = list(loaded_model.feature_names_in_)
        st.info("Using model.feature_names_in_ for expected columns.")
    elif feature_cols:
        expected = list(feature_cols)
        st.info("Using saved feature_cols for expected columns.")

    if expected is None or len(expected) == 0:
        st.error("Model does not expose expected feature names. "
                 "Best practice: save and load a sklearn Pipeline that includes preprocessing.")
    else:
        # Check missing/extra columns
        missing_cols = [c for c in expected if c not in future_df.columns]
        extra_cols   = [c for c in future_df.columns if c not in expected]

        if missing_cols:
            st.error(f"❌ Your uploaded file is missing required columns: {missing_cols}")
        else:
            # Build X_new matching the training schema and order
            X_new = future_df.reindex(columns=expected).copy()

            # Quick diagnostics before predict
            st.write("X_new shape:", X_new.shape)
            st.write("X_new dtypes:", X_new.dtypes)
            st.write("Missing by column:", X_new.isna().sum())

            # If you trained WITHOUT a preprocessing Pipeline, you must ensure all features are numeric.
            # Try to coerce numeric columns; leave true categoricals untouched (Pipeline should handle them).
            # If you did not use a Pipeline and have categoricals, prediction will still fail—warn the user.
            numeric_like = []
            if hasattr(loaded_model, "named_steps"):  # likely a Pipeline -> preprocessing will handle types
                pass
            else:
                # Heuristic: try to coerce everything; non-numeric will become NaN and we replace below.
                for c in X_new.columns:
                    before = X_new[c].copy()
                    X_new[c] = pd.to_numeric(X_new[c], errors="coerce")
                    if X_new[c].dtype != "float64" and X_new[c].dtype != "int64":
                        # still non-numeric; restore
                        X_new[c] = before
                    else:
                        numeric_like.append(c)

                # If any non-numeric columns remain, warn that a preprocessing Pipeline is required
                non_numeric_cols = [c for c in X_new.columns if not np.issubdtype(X_new[c].dtype, np.number)]
                if non_numeric_cols:
                    st.warning(
                        "Your model file appears to be a raw estimator without preprocessing. "
                        "Non-numeric columns present: "
                        f"{non_numeric_cols}. "
                        "Either (a) re-train/switch to a saved sklearn Pipeline that encodes these, "
                        "or (b) upload a template where these columns are already one-hot/encoded exactly as in training."
                    )

            # Replace inf/NaN for safety (align with your training imputation strategy)
            X_new = X_new.replace([np.inf, -np.inf], np.nan).fillna(0)

            # STEP 3 — PREDICTIONS
            st.header("Step 3️⃣ — Generate Predictions")
            if st.button("Predict Future Outcomes"):
                try:
                    preds = loaded_model.predict(X_new)
                    future_df["Predicted_" + target_col] = preds
                    st.success("✅ Predictions complete!")
                    st.dataframe(future_df)
                    st.download_button(
                        "📥 Download Predictions CSV",
                        future_df.to_csv(index=False),
                        file_name="future_predictions.csv"
                    )
                except Exception as e:
                    st.error("❌ Prediction failed.")
                    st.exception(e)
                    st.info(
                        "If this is a raw model (not a Pipeline), ensure your uploaded CSV has the exact encoded "
                        "numeric feature set used at training time (same one-hot columns, same order)."
                    )
