import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv
import requests

# Load .env variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
ELEVEN_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# Use Rachel's voice ID (default from ElevenLabs)
VOICE_ID = "EXAVITQu4vr4xnSDxMaL"

# ---- Generate Script with Gemini ----
def generate_script_gemini(mood, topic):
    prompt = f"""
    Create a short, engaging, and emotional audio script under 100 words in a {mood} tone 
    on the topic "{topic}". This is for a daily voice note experience in an audio streaming app. 
    It should feel warm, human, and encouraging.
    """
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content(prompt)
    return response.text.strip()

# ---- Convert to Voice using ElevenLabs ----
def generate_audio(script_text):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    
    headers = {
        "xi-api-key": ELEVEN_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "text": script_text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        audio_path = "ai_audio.mp3"
        with open(audio_path, "wb") as f:
            f.write(response.content)
        return audio_path
    else:
        st.error(f"❌ Audio generation failed. Status {response.status_code}: {response.text}")
        return None

# ---- Streamlit UI ----
st.set_page_config(page_title="Kuku AI Companion", layout="centered")
st.title("🎧 Kuku AI Companion")
st.caption("Your AI-generated voice content based on mood and interest")

mood = st.selectbox("What's your mood today?", ["motivation", "calm", "learning"])
topic = st.text_input("Enter a topic you’d like to hear about:", value="mindfulness")

if st.button("🎙️ Generate My AI Audio"):
    with st.spinner("✨ Crafting your personalized voice note..."):
        script = generate_script_gemini(mood, topic)
        st.success("📝 Script Generated!")
        st.text_area("Generated Script", script, height=150)

        st.info("🔊 Generating voice with ElevenLabs...")
        audio_path = generate_audio(script)

        if audio_path:
            st.audio(audio_path, format="audio/mp3")
            st.download_button("⬇️ Download Audio", data=open(audio_path, "rb"), file_name="kuku_ai_voice.mp3")

st.markdown("---")
st.caption("Prototype Demo | Built with Gemini + ElevenLabs + Streamlit")
