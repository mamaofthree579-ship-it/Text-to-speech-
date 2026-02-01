import streamlit as st
from gtts import gTTS
import io
import re

st.title("Custom Prosody TTS Engine")

text = st.text_area("Input Text", "Resonant harmonic fields stabilize structure")

st.subheader("Profile Preset")

profile = st.selectbox(
    "Profile",
    ["Custom", "Slow Chant"]
)

# -------- Defaults -------- #

bpm = 130
style = "neutral"
vowel_mode = "normal"
cluster_pause = 40
repeat_pause = 60
stress_first = True
repeat_count = 1
chant_mode = False

# -------- Preset Override -------- #

if profile == "Slow Chant":
    bpm = 70
    style = "legato"
    vowel_mode = "long"
    cluster_pause = 180
    repeat_pause = 300
    stress_first = True
    chant_mode = True

# -------- Custom Controls -------- #

if profile == "Custom":

    bpm = st.slider("Tempo BPM", 60, 220, 130)

    style = st.selectbox(
        "Style",
        ["legato", "neutral", "clipped", "staccato"]
    )

    vowel_mode = st.selectbox(
        "Vowel Length",
        ["normal", "short", "long"]
    )

    cluster_pause = st.slider("Cluster Pause ms", 0, 250, 40)
    repeat_pause = st.slider("Repeat Pause ms", 0, 400, 60)
    stress_first = st.checkbox("Stress first cluster", True)
    repeat_count = st.slider("Repetitions", 1, 5, 1)

# -------- Prosody Engine -------- #

def elongate_vowels(t):
    if vowel_mode != "long":
        return t
    return re.sub(r"([aeiou])", r"\1\1", t)

def shorten_vowels(t):
    if vowel_mode != "short":
        return t
    return re.sub(r"([aeiou])", r"\1'", t)

def chant_transform(t):
    words = t.split()
    grouped = []
    for w in words:
        grouped.append(w + " ~")
    return " ".join(grouped)

def style_transform(t):
    words = t.split()

    if style == "staccato":
        return ". ".join(words)

    if style == "clipped":
        return "! ".join(words)

    return " ".join(words)

def stress_transform(t):
    if not stress_first:
        return t
    words = t.split()
    if words:
        words[0] = words[0].upper()
    return " ".join(words)

def ms_to_pause(ms):
    dots = max(1, ms // 250)
    return ". " * dots

# -------- Build Text -------- #

processed = text
processed = elongate_vowels(processed)
processed = shorten_vowels(processed)
processed = style_transform(processed)
processed = stress_transform(processed)

if chant_mode:
    processed = chant_transform(processed)

cluster_gap = ms_to_pause(cluster_pause)
repeat_gap = ms_to_pause(repeat_pause)

final_text = (processed + cluster_gap + repeat_gap) * repeat_count

st.subheader("Prosody Output Text")
st.write(final_text)

# -------- Generate -------- #

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
            "chant_speech.mp3",
            "audio/mp3"
        )

        st.success("Generated with selected profile")

    except Exception as e:
        st.error(str(e))
