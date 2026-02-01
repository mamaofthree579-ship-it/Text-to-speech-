import streamlit as st
from gtts import gTTS
import io
import re
import numpy as np
import matplotlib.pyplot as plt

st.title("Custom Prosody TTS with Spectrogram")

text = st.text_area(
    "Input Text",
    "Trade: hello world | Ritual: chant long vowels"
)

st.subheader("Profile Preset")
profile = st.selectbox("Profile", ["Custom", "Slow Chant"])

# ---------- Defaults ----------
bpm = 130
style = "neutral"
vowel_mode = "normal"
cluster_pause = 40
repeat_pause = 60
stress_first = True
repeat_count = 1
chant_style = False
use_tilde = False

# ---------- Preset Overrides ----------
if profile == "Slow Chant":
    bpm = 70
    style = "legato"
    vowel_mode = "long"
    cluster_pause = 180
    repeat_pause = 300
    stress_first = True
    chant_style = True
    use_tilde = True

# ---------- User Adjustable ----------
st.subheader("Adjust Parameters")
bpm = st.slider("TEMPO (BPM)", 60, 220, bpm)
style = st.selectbox("STYLE", ["legato","neutral","clipped","staccato"], index=["legato","neutral","clipped","staccato"].index(style))
vowel_mode = st.selectbox("VOWEL LENGTH", ["normal","short","long"], index=["normal","short","long"].index(vowel_mode))
cluster_pause = st.slider("PAUSE BETWEEN CLUSTERS (ms)", 0, 250, cluster_pause)
repeat_pause = st.slider("PAUSE BETWEEN REPETITIONS (ms)", 0, 400, repeat_pause)
stress_first = st.checkbox("Primary stress on first cluster", stress_first)
repeat_count = st.slider("Repetitions", 1, 5, repeat_count)
use_tilde = st.checkbox("Use tildes for chanting", use_tilde)
show_spec = st.checkbox("Generate Spectrogram")

# ---------- Prosody Engine ----------
def elongate_vowels(t):
    if vowel_mode=="long":
        return re.sub(r"([aeiou])", r"\1\1", t)
    return t

def shorten_vowels(t):
    if vowel_mode=="short":
        return re.sub(r"([aeiou])", r"\1'", t)
    return t

def style_transform(t):
    words = t.split()
    if style=="staccato":
        return ". ".join(words)
    if style=="clipped":
        return "! ".join(words)
    return " ".join(words)

def stress_transform(t):
    if stress_first:
        words = t.split()
        if words:
            words[0] = words[0].upper()
        return " ".join(words)
    return t

def chant_transform(t):
    if use_tilde:
        words = t.split()
        return " ~ ".join(words)
    return t

def ms_to_pause(ms):
    dots = max(1, ms//250)
    return ". "*dots

# ---------- Build Processed Text ----------
processed = text
processed = elongate_vowels(processed)
processed = shorten_vowels(processed)
processed = style_transform(processed)
processed = stress_transform(processed)
processed = chant_transform(processed)

cluster_gap = ms_to_pause(cluster_pause)
repeat_gap = ms_to_pause(repeat_pause)
final_text = (processed + cluster_gap + repeat_gap) * repeat_count

st.subheader("Processed Text")
st.write(final_text)

# ---------- Generate TTS ----------
if st.button("Generate Speech"):
    try:
        tts = gTTS(final_text, slow=(bpm<110))
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        audio_bytes = buf.getvalue()

        st.audio(audio_bytes)
        st.download_button("Download Audio", audio_bytes, "prosody_speech.mp3", "audio/mp3")

        st.success("Generated with profile & custom parameters")

        # ---------- Spectrogram ----------
        if show_spec:
            # Convert bytes to numeric array (simulate waveform)
            data = np.frombuffer(audio_bytes[:50000], dtype=np.uint8)
            cluster_labels = []
            # Simple simulation: label ~ for ritual, | or text for trade
            for word in final_text.split():
                if "~" in word or vowel_mode=="long":
                    cluster_labels.append(1)  # ritual
                else:
                    cluster_labels.append(0)  # trade

            fig, ax = plt.subplots(figsize=(10,3))
            ax.specgram(data, Fs=8000, NFFT=256, noverlap=128, cmap="Blues")
            # Overlay color bars
            for idx, label in enumerate(cluster_labels):
                color = "orange" if label==1 else "blue"
                ax.axvspan(idx*50, (idx+1)*50, facecolor=color, alpha=0.2)

            ax.set_title("Spectrogram (Blue=Trade, Orange=Ritual)")
            st.pyplot(fig)

    except Exception as e:
        st.error(str(e))
