import streamlit as st
import pandas as pd
from phonemizer import phonemize
from TTS.api import TTS
import soundfile as sf
from tempfile import NamedTemporaryFile

st.title("Phoneme-Level Text-to-Speech Generator")

# --- User Input ---
text_input = st.text_area("Enter Text:", "Hello world!")

if text_input.strip():

    # --- Convert text to phonemes ---
    phonemes = phonemize(text_input, language='en-us', backend='espeak', strip=True)
    phoneme_list = phonemes.split()
    
    st.subheader("Phoneme Breakdown")
    st.write(phoneme_list)

    # --- Create editable DataFrame for phoneme timing ---
    df = pd.DataFrame({
        "Phoneme": phoneme_list,
        "Duration (s)": [0.2] * len(phoneme_list)  # default 0.2s per phoneme
    })

    edited_df = st.experimental_data_editor(df, num_rows="dynamic")

    # --- Generate Speech Button ---
    if st.button("Generate Speech"):
        # Convert durations to list
        durations = edited_df["Duration (s)"].tolist()

        # Load TTS model
        tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False)

        # Generate speech with phoneme-level durations
        with NamedTemporaryFile(delete=False, suffix=".wav") as f:
            output_file = f.name

        tts.tts_to_file(
            phonemes=" ".join(phoneme_list),
            file_path=output_file,
            speaker=None,   # default speaker
            phoneme_durations=durations  # specify duration per phoneme
        )

        # --- Playback ---
        st.audio(output_file, format="audio/wav")
        st.success("Speech generated! Play above or download below.")

        st.download_button(
            label="Download Speech",
            data=open(output_file, "rb").read(),
            file_name="tts_output.wav",
            mime="audio/wav"
        )
