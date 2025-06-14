import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor

from shared_utils import get_connection, quote_table
from ui_utils import render_page_header, render_instructions_block

render_page_header("Prediction Engine PRO", "🔮 Build your own custom prediction model")

render_instructions_block("""
**Workflow:**
1️⃣ Select a table that includes historical fantasy data  
2️⃣ Choose your prediction target (usually `fantasy_points`)  
3️⃣ Select the features you believe influence the target (passing_yards, carries, receptions, etc)  
4️⃣ Train model to estimate fantasy performance in future games  
5️⃣ Export model and use predictions for weekly forecasting
""")

# Setup model save path
os.makedirs("models", exist_ok=True)

# Load available tables
conn = get_connection()
tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn)
conn.close()

selected_table = st.selectbox("Select dataset for modeling", tables["name"].tolist() if not tables.empty else ["No tables found"])

if selected_table != "No tables found":
    conn = get_connection()
    df = pd.read_sql(f"SELECT * FROM {quote_table(selected_table)}", conn)
    conn.close()

    st.write("Sample of selected data:")
    st.dataframe(df.head())

    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    feature_cols = st.multiselect("Select input features (X)", numeric_cols)
    target_col = st.selectbox("Select target column (y)", numeric_cols, index=numeric_cols.index("fantasy_points") if "fantasy_points" in numeric_cols else 0)

    if feature_cols and target_col:
        X = df[feature_cols].fillna(0)
        y = df[target_col].fillna(0)

        test_size = st.slider("Test Set Size (%)", 10, 40, 20, step=5)
        n_estimators = st.slider("Random Forest: n_estimators", 50, 500, 200, 50)
        max_depth = st.slider("Random Forest: max_depth", 3, 20, 10, 1)

        if st.button("Train Model"):
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size/100, random_state=42)

            model = RandomForestRegressor(n_estimators=n_estimators, max_depth=max_depth, random_state=42)
            model.fit(X_train, y_train)

            preds = model.predict(X_test)
            rmse = mean_squared_error(y_test, preds, squared=False)
            r2 = r2_score(y_test, preds)

            st.success(f"✅ Model Trained!  RMSE: {rmse:.2f}  |  R²: {r2:.2%}")

            # Save model
            model_file = f"models/{selected_table}_fantasy_predictor.pkl"
            joblib.dump((model, feature_cols, target_col), model_file)
            st.info(f"Model saved as {model_file}")

            # Plot prediction scatter
            fig, ax = plt.subplots()
            sns.scatterplot(x=y_test, y=preds, ax=ax)
            ax.plot([y.min(), y.max()], [y.min(), y.max()], '--', color='gray')
            ax.set_xlabel("Actual")
            ax.set_ylabel("Predicted")
            st.pyplot(fig)

            # Download predictions
            pred_df = pd.DataFrame({"Actual": y_test, "Predicted": preds})
            st.download_button("📥 Download Predictions", pred_df.to_csv(index=False), file_name="predictions.csv")
