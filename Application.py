import streamlit as st
from gtts import gTTS
import io
import re

st.title("Text-to-Speech Timing App")

st.write("Use [pause=500] to insert pauses in milliseconds.")

text = st.text_area(
    "Enter text",
    "Hello there [pause=400] this is timed speech"
)

slow_mode = st.checkbox("Slow pacing")

def synth_chunk(chunk):
    tts = gTTS(chunk)
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    return buf.getvalue()

if st.button("Generate Speech") and text.strip():

    parts = re.split(r"\[pause=(\d+)\]", text)

    audio_bytes = b""

    for i, part in enumerate(parts):
        if i % 2 == 0:
            if part.strip():
                audio_bytes += synth_chunk(part)
        else:
            # pause marker — add silence by repeating tiny silent mp3 frame
            pause_ms = int(part)
            silence = b"\x00" * (pause_ms * 2)
            audio_bytes += silence

    st.audio(audio_bytes, format="audio/mp3")

    st.download_button(
        "Download",
        data=audio_bytes,
        file_name="speech.mp3",
        mime="audio/mp3"
    )
