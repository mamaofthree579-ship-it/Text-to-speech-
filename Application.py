import streamlit as st
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import io
import pandas as pd

st.title("Text-to-Speech with Timing Control")

text = st.text_area("Enter text")

speed = st.slider("Speech Speed Multiplier", 0.5, 2.0, 1.0)
pause_ms = st.slider("Pause Between Words (ms)", 0, 800, 150)

if st.button("Generate Speech") and text.strip():

    words = text.split()

    combined = AudioSegment.empty()

    for word in words:
        tts = gTTS(word)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)

        segment = AudioSegment.from_file(buf, format="mp3")

        # adjust speed
        segment = segment._spawn(
            segment.raw_data,
            overrides={"frame_rate": int(segment.frame_rate * speed)}
        ).set_frame_rate(segment.frame_rate)

        combined += segment
        combined += AudioSegment.silent(duration=pause_ms)

    output_buf = io.BytesIO()
    combined.export(output_buf, format="mp3")

    st.audio(output_buf.getvalue(), format="audio/mp3")

    st.download_button(
        "Download Audio",
        data=output_buf.getvalue(),
        file_name="speech.mp3",
        mime="audio/mp3"
    )
