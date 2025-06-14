import streamlit as st

# Universal Filtering Logic
def apply_universal_filters(df):
    filtered_df = df.copy()

    # Season filter (if exists)
    if "season" in df.columns:
        seasons = sorted(df["season"].dropna().unique())
        season_range = st.slider("Season Range", min(seasons), max(seasons), (min(seasons), max(seasons)))
        filtered_df = filtered_df[filtered_df["season"].between(*season_range)]

    # Player filter (if exists)
    if "player_name" in df.columns:
        player_search = st.text_input("Search by Player Name")
        if player_search:
            filtered_df = filtered_df[filtered_df["player_name"].str.contains(player_search, case=False, na=False)]

    # Position filter (if exists)
    if "position" in df.columns:
        positions = sorted(df["position"].dropna().unique())
        selected_positions = st.multiselect("Position Filter", positions, default=positions)
        filtered_df = filtered_df[filtered_df["position"].isin(selected_positions)]

    st.write(f"Filtered rows: {len(filtered_df)}")
    return filtered_df
