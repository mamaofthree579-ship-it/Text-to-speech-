import streamlit as st
from gtts import gTTS
import io
import re

st.title("Custom Prosody TTS Engine")

text = st.text_area("Input Text", "Resonant systems stabilize matter")

st.subheader("Performance Profile")

bpm = st.slider("TEMPO (BPM)", 60, 220, 130)

style = st.selectbox(
    "STYLE",
    ["legato", "neutral", "clipped", "staccato"]
)

vowel_mode = st.selectbox(
    "VOWEL LENGTH",
    ["normal", "short"]
)

cluster_pause = st.slider(
    "PAUSE BETWEEN CLUSTERS (ms)",
    0, 200, 40
)

repeat_pause = st.slider(
    "PAUSE BETWEEN REPETITIONS (ms)",
    0, 300, 60
)

stress_first = st.checkbox("Primary stress on first cluster", True)

repeat_count = st.slider("Repetitions", 1, 5, 1)

# ---------- Prosody Engine ---------- #

def bpm_to_word_pause(bpm):
    beat_ms = 60000 / bpm
    return int(beat_ms * 0.5)

def apply_vowel_shortening(t):
    if vowel_mode == "short":
        return re.sub(r"([aeiou])", r"\1'", t)
    return t

def apply_style_segmentation(t):
    words = t.split()

    if style == "staccato":
        return " | ".join(words)

    if style == "clipped":
        return ". ".join(words)

    if style == "legato":
        return " ".join(words)

    return t

def apply_stress(t):
    if not stress_first:
        return t
    words = t.split()
    if words:
        words[0] = words[0].upper() + "!"
    return " ".join(words)

def ms_to_punctuation(ms):
    dots = max(1, ms // 250)
    return ". " * dots

# ---------- Build Output Text ---------- #

processed = text
processed = apply_vowel_shortening(processed)
processed = apply_style_segmentation(processed)
processed = apply_stress(processed)

cluster_gap = ms_to_punctuation(cluster_pause)
repeat_gap = ms_to_punctuation(repeat_pause)

processed = processed.replace("|", cluster_gap)

final_text = (processed + repeat_gap) * repeat_count

st.subheader("Generated Prosody Text")
st.write(final_text)

# ---------- Generate ---------- #

if st.button("Generate Speech"):

    try:
        tts = gTTS(final_text, slow=(bpm < 110))
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        audio = buf.getvalue()

        st.audio(audio)

        st.download_button(
            "Download Audio",
            audio,
            "prosody_speech.mp3",
            "audio/mp3"
        )

        st.success("Generated with custom prosody profile")

    except Exception as e:
        st.error(str(e))
