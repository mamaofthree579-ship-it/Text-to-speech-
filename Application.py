import streamlit as st
from gtts import gTTS
import io
import re

st.title("Text-to-Speech Timing App")

st.write("Insert pauses with: [pause=500] (milliseconds)")

text = st.text_area(
    "Enter text",
    "Hello there [pause=600] this system is working."
)

speed_style = st.selectbox(
    "Speech pacing",
    ["Normal", "Slow", "Very Slow"]
)

def expand_pauses(t):
    def repl(match):
        ms = int(match.group(1))
        # convert ms to punctuation pauses gTTS understands
        dots = max(1, ms // 250)
        return ". " * dots
    return re.sub(r"\[pause=(\d+)\]", repl, t)

if st.button("Generate Speech"):

    if not text.strip():
        st.warning("Enter text first.")
        st.stop()

    processed = expand_pauses(text)

    slow_flag = speed_style != "Normal"

    try:
        tts = gTTS(processed, slow=slow_flag)
        buf = io.BytesIO()
        tts.write_to_fp(buf)

        audio_bytes = buf.getvalue()

        st.audio(audio_bytes, format="audio/mp3")

        st.download_button(
            "Download Audio",
            data=audio_bytes,
            file_name="speech.mp3",
            mime="audio/mp3"
        )

        st.success("Speech generated successfully.")

    except Exception as e:
        st.error(f"TTS failed: {e}")
