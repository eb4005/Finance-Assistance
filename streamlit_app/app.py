import streamlit as st
import requests
import base64

st.set_page_config(page_title="Finance Briefing Assistant", layout="centered")

st.title(" Multi-Agent Finance Assistant")

option = st.radio("Choose input method:", ("Text Query", "Voice Upload"))

# ORCHESTRATOR_URL = "http://localhost:8000"
ORCHESTRATOR_URL = "http://orchestrator:8000"


if option == "Text Query":
    query = st.text_input("Enter your query", "What's our Asia tech exposure?")
    if st.button("Generate Brief"):
        with st.spinner("Generating summary..."):
            response = requests.post(
                f"{ORCHESTRATOR_URL}/brief", json={"user_query": query}
            )
            if response.status_code == 200:
                result = response.json()
                st.success("Summary:")
                st.write(result.get("summary"))
            else:
                st.error("Failed to generate summary.")

else:
    uploaded_file = st.file_uploader("Upload your voice (MP3/WAV)", type=["mp3", "wav"])
    if uploaded_file is not None and st.button("Process Voice Query"):
        with st.spinner("Processing audio and generating brief..."):
            files = {'audio': (uploaded_file.name, uploaded_file, uploaded_file.type)}
            response = requests.post(f"{ORCHESTRATOR_URL}/voice-brief", files=files)
            if response.status_code == 200:
                result = response.json()
                st.success(f"Transcribed Query: {result['query']}")
                st.write("**Summary:**")
                st.write(result.get("summary"))

                # Play the audio if available
                audio_base64 = result.get("audio_base64")
                if audio_base64:
                    st.audio(base64.b64decode(audio_base64), format="audio/wav")
            else:
                st.error("Voice processing failed.")
