import streamlit as st
import pandas as pd
from shared_utils import get_connection

st.header("🔗 Universal Data Fusion Engine 4.0")

st.markdown("""
This module dynamically merges all uploaded tables into a single enriched dataset ready for full analysis, filtering, prediction & visualization.

- Automatically detects which tables exist in your database.
- Merges on common keys: player_id, week, season, game_id, stadium_id.
- Produces a fully enriched master dataset.
""")

# Connect to DB
conn = get_connection()
existing_tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn)["name"].tolist()

# Dynamically load any existing tables
dfs = {}

for table in ["player_stats", "injuries", "weather", "stadiums", "games"]:
    if table in existing_tables:
        dfs[table] = pd.read_sql(f"SELECT * FROM {table}", conn)
        st.write(f"✅ Loaded table: {table} ({len(dfs[table])} rows)")
    else:
        st.write(f"⚠️ Table not found: {table}")

# Begin dynamic joins
df_final = None

if "player_stats" in dfs:
    df_final = dfs["player_stats"]

    if "injuries" in dfs:
        df_final = df_final.merge(
            dfs["injuries"],
            on=["player_id", "season", "week"],
            how="left"
        )

    if "games" in dfs:
        df_final = df_final.merge(
            dfs["games"],
            on=["season", "week"],
            how="left"
        )

    if "weather" in dfs and "games" in dfs:
        df_final = df_final.merge(
            dfs["weather"],
            on=["game_id"],
            how="left"
        )

    if "stadiums" in dfs and "games" in dfs:
        df_final = df_final.merge(
            dfs["stadiums"],
            on=["stadium_id"],
            how="left"
        )

if df_final is not None:
    st.success(f"✅ Merged final dataset: {len(df_final)} rows")
    st.dataframe(df_final.head())

    # Optionally save to DB as master table
    save_name = st.text_input("Save unified dataset as table name:", value="unified_master_dataset")
    if st.button("💾 Save Unified Table"):
        df_final.to_sql(save_name, conn, if_exists="replace", index=False)
        st.success(f"✅ Saved unified dataset as '{save_name}'")

else:
    st.warning("No primary 'player_stats' table loaded — cannot generate master dataset.")

conn.close()
