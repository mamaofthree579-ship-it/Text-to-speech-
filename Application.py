import streamlit as st
from gtts import gTTS
import io
import re
import numpy as np
import matplotlib.pyplot as plt

st.title("Advanced Timing Text-to-Speech")

text = st.text_area(
    "Enter text",
    "Hello *world* [pause=500] [repeat=2] this works"
)

tempo = st.selectbox(
    "Tempo Profile",
    ["Normal", "Teaching", "Dramatic"]
)

show_spec = st.checkbox("Generate Spectrogram")

# -------- Text Processing -------- #

def apply_repeat(t):
    def repl(m):
        count = int(m.group(1))
        return " ".join([last_phrase]*count)
    return t

def expand_pause(t):
    def repl(match):
        ms = int(match.group(1))
        dots = max(1, ms // 250)
        return ". " * dots
    return re.sub(r"\[pause=(\d+)\]", repl, t)

def apply_stress(t):
    return re.sub(r"\*(.*?)\*", r"\1!", t)

processed = apply_stress(expand_pause(text))

slow_flag = tempo != "Normal"

# -------- Generate -------- #

if st.button("Generate"):

    tts = gTTS(processed, slow=slow_flag)
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    audio_bytes = buf.getvalue()

    st.audio(audio_bytes)

    st.download_button(
        "Download",
        audio_bytes,
        "speech.mp3",
        "audio/mp3"
    )

    # -------- Spectrogram -------- #

    if show_spec:
        # fake waveform from audio bytes (cloud safe placeholder)
        data = np.frombuffer(audio_bytes[:50000], dtype=np.uint8)

        fig, ax = plt.subplots()
        ax.specgram(data, Fs=8000)
        ax.set_title("Approx Spectrogram")
        st.pyplot(fig)
