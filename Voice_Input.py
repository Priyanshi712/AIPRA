"""
voice_input.py
================
Voice input module for AIPRA.

Lets the user record a short voice clip directly in the browser and
turns it into text using the free Google Web Speech API (via the
`SpeechRecognition` library). No API key required, but it does need
an internet connection at transcription time.

Install:
    pip install streamlit-mic-recorder SpeechRecognition

Usage (inside app.py):
    from voice_input import get_voice_query
    voice_text = get_voice_query()
"""

import io
import streamlit as st

try:
    from streamlit_mic_recorder import mic_recorder
    _MIC_AVAILABLE = True
except ImportError:
    _MIC_AVAILABLE = False

try:
    import speech_recognition as sr
    _SR_AVAILABLE = True
except ImportError:
    _SR_AVAILABLE = False


def _transcribe(audio_bytes: bytes) -> str:
    """Transcribe raw WAV audio bytes to text using Google's free web API."""
    recognizer = sr.Recognizer()

    with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
        audio = recognizer.record(source)

    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        raise RuntimeError(f"Speech recognition service error: {e}")


def get_voice_query():
    """
    Renders a mic-recorder widget and returns transcribed text once the
    user finishes recording.

    Returns:
        str: the transcribed text, or
        None: if nothing has been recorded yet, no speech was detected,
              or the required packages aren't installed.
    """

    if not _MIC_AVAILABLE or not _SR_AVAILABLE:
        st.warning(
            "Voice input needs two extra packages. Install them with:\n\n"
            "`pip install streamlit-mic-recorder SpeechRecognition`"
        )
        return None

    st.caption("🎤 Tap to record your research question, tap again to stop.")

    audio = mic_recorder(
        start_prompt="● Start recording",
        stop_prompt="■ Stop recording",
        just_once=True,
        use_container_width=True,
        format="wav",
        key="aipra_mic_recorder"
    )

    if audio is None:
        return None

    with st.spinner("Transcribing..."):
        try:
            text = _transcribe(audio["bytes"])
        except RuntimeError as e:
            st.error(str(e))
            return None

    if not text:
        st.warning("Couldn't make out any speech — please try again.")
        return None

    st.success(f"Heard: \u201c{text}\u201d")
    return text