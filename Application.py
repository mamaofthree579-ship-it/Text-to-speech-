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

        # ---------- Spectrogram Simulation ----------
        if show_spec:
            # Create synthetic waveform: consonant bursts + vowel sustains
            sample_rate = 8000
            duration_per_word = 0.4  # seconds per word
            consonant_duration = 0.05

            words = final_text.split()
            waveform = np.array([], dtype=np.float32)
            colors = []

            for word in words:
                # Consonant burst
                cons_samples = np.random.uniform(-1,1,int(consonant_duration*sample_rate))
                waveform = np.concatenate([waveform, cons_samples])
                
                # Vowel sustain based on vowel_mode
                vowel_len = {"short":0.1,"normal":0.2,"long":0.35}
                vowel_samples = np.random.uniform(-0.3,0.3,int(vowel_len.get(vowel_mode,"normal")*sample_rate))
                waveform = np.concatenate([waveform, vowel_samples])

                # Cluster type
                if "~" in word or vowel_mode=="long":
                    colors.append("orange")  # ritual
                else:
                    colors.append("blue")    # trade

            # Generate spectrogram
            fig, ax = plt.subplots(figsize=(12,4))
            Pxx, freqs, bins, im = ax.specgram(waveform, Fs=sample_rate, NFFT=256, noverlap=128, cmap="Greys")

            # Overlay color-coded blocks
            current_sample = 0
            for idx, word in enumerate(words):
                total_samples = int(duration_per_word*sample_rate)
                color = colors[idx]
                ax.axvspan(current_sample/sample_rate, (current_sample+total_samples)/sample_rate, facecolor=color, alpha=0.2)
                current_sample += total_samples

            ax.set_title("Spectrogram (Blue=Trade, Orange=Ritual) | Consonant Peaks & Vowel Length Shown")
            ax.set_ylabel("Frequency [Hz]")
            ax.set_xlabel("Time [s]")
            st.pyplot(fig)

    except Exception as e:
        st.error(str(e))
