
import streamlit as st
import pandas as pd

# Load the music library
song_library = pd.read_csv("jay_music_library.csv")

# Normalize column names
song_library.columns = song_library.columns.str.strip().str.lower()

def get_compatible_keys(current_key, key_range):
    key_number = int(current_key[:-1])
    key_letter = current_key[-1]
    return [f"{((key_number + i - 1) % 12 or 12)}{key_letter}" for i in range(-key_range, key_range + 1)]

st.set_page_config(layout="wide")
st.title("🎧 AI DJ Mix Recommender")

song_choice = st.selectbox("Pick the song you're currently playing:", song_library["title"])

if song_choice:
    current_song = song_library[song_library["title"] == song_choice].iloc[0]
    current_bpm = float(current_song["bpm"])
    current_key = current_song["key"]
    current_energy = float(current_song["energy"])

    # Filters
    st.sidebar.subheader("🎚 Filters")
    bpm_range = st.sidebar.slider("± BPM Range", 1, 20, 5)
    key_range = st.sidebar.slider("± Key Steps", 0, 3, 1)
    energy_range = st.sidebar.slider("Energy Level", 1.0, 10.0, (max(1.0, current_energy - 1), min(10.0, current_energy + 1)), step=0.1)

    compatible_keys = get_compatible_keys(current_key, key_range)

    recommendations = song_library[
        (song_library["bpm"].between(current_bpm - bpm_range, current_bpm + bpm_range)) &
        (song_library["key"].isin(compatible_keys)) &
        (song_library["title"] != song_choice) &
        (song_library["energy"].between(energy_range[0], energy_range[1]))
    ].copy()

    # Add matching score to sort by best matches
    recommendations["bpm_diff"] = (recommendations["bpm"] - current_bpm).abs()
    recommendations["key_match"] = (recommendations["key"] == current_key).astype(int)
    recommendations = recommendations.sort_values(by=["key_match", "bpm_diff"], ascending=[False, True])

    # Display total count
    st.subheader(f"🎵 Recommended Songs to Mix In: ({len(recommendations)} matches)")
    st.dataframe(recommendations[["title", "artist", "bpm", "key", "energy"]].reset_index(drop=True), use_container_width=True)
