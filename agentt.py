import streamlit as st
import os
import sys
import speech_recognition as sr
from gtts import gTTS
import base64
from io import BytesIO
import streamlit.components.v1 as components
import tempfile


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from state_agent import SchemeAgent
from agent_tools import search_scheme_tool


st.set_page_config(
    page_title="SchemeKhoj - Voice Agent",
    page_icon="🎙️",
    layout="wide"
)


st.markdown("""
<style>
.stApp { background-color: #f0f2f6; }

.main-title {
    font-size: 3rem;
    color: #FF9933;
    text-align: center;
    font-weight: 800;
    margin-bottom: 10px;
}
.sub-title {
    text-align: center;
    color: #555;
    font-size: 1.2rem;
    margin-bottom: 30px;
}
[data-testid="stChatMessage"] {
    background-color: #ffffff !important;
    border: 1px solid #e0e0e0;
    border-radius: 12px;
    padding: 15px;
    margin-bottom: 10px;
}
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


with st.sidebar:
    st.title("🇮🇳 SchemeKhoj AI")
    st.markdown("हिंदी में सरकारी योजनाओं की जानकारी (Government Schemes in Hindi).")
    
    st.markdown("---")
    st.markdown("**💡 Quick Try (जल्दी आज़माएं):**")
    
    if st.button("🌾 किसान कर्ज (Farmer Loans)"):
        st.session_state.user_input = "किसानों के लिए लोन योजना बताओ"
        
    if st.button("🎓 छात्रवृत्ति (Scholarships)"):
        st.session_state.user_input = "छात्रों के लिए स्कॉलरशिप"
        
    if st.button("👩‍💼 महिला योजना (Women Schemes)"):
        st.session_state.user_input = "महिलाओं के लिए बिजनेस लोन"
        
    st.markdown("---")
    st.header("📝 Evaluation Logs")
    st.caption("Download chat history for assignment submission.")

    transcript = ""
    if "messages" in st.session_state:
        for msg in st.session_state.messages:
            transcript += f"[{msg['role'].upper()}]: {msg['content']}\n\n"

    st.download_button(
        label="📥 Download Transcript",
        data=transcript,
        file_name="evaluation_transcript.txt",
        mime="text/plain"
    )

def text_to_speech_player(text, lang="hi"):
    """
    Generates audio once and provides play/pause + speed control bar.
    """
    tts = gTTS(text=text, lang=lang)
    fp = BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    audio_b64 = base64.b64encode(fp.read()).decode()

    components.html(
        f"""
        <audio id="audioPlayer" controls style="width:100%; margin-top:10px;">
            <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
        </audio>

        <div style="margin-top:6px;">
            <label><b>🔊 Speed:</b></label>
            <input type="range" min="0.5" max="2.0" value="1.0" step="0.1"
                oninput="
                    const audio = document.getElementById('audioPlayer');
                    audio.playbackRate = this.value;
                    document.getElementById('rateVal').innerText = this.value + 'x';
                ">
            <span id="rateVal">1.0x</span>
        </div>
        """,
        height=130
    )


def recognize_speech_from_mic():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 बोलिए...")
        r.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = r.listen(source, timeout=8, phrase_time_limit=6)
            return r.recognize_google(audio, language="hi-IN")
        except:
            return None

if "state_agent" not in st.session_state:
    st.session_state.state_agent = SchemeAgent()


if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "नमस्ते! मैं स्कीम-सेतु हूँ। बोलकर पूछिए।"
    }]


st.markdown('<div class="main-title">🎙️ SchemeKhoj Voice Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Bolkar Yojnayein Khojein</div>', unsafe_allow_html=True)


for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


col1, col2 = st.columns([1, 4])

with col1:
    if st.button("🎤 TAP TO SPEAK"):
        voice_text = recognize_speech_from_mic()
        if voice_text:
            st.session_state.user_input = voice_text

with col2:
    text_input = st.chat_input("... या यहाँ टाइप करें")
    if text_input:
        st.session_state.user_input = text_input


if "user_input" in st.session_state:
    user_query = st.session_state.user_input
    del st.session_state.user_input

    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    result = st.session_state.state_agent.step(user_query)

    if isinstance(result, dict) and result.get("action") == "SEARCH":
        output_text = search_scheme_tool(result["query"])
    else:
        output_text = result

    with st.chat_message("assistant"):
        st.markdown(output_text)
        text_to_speech_player(output_text)

    st.session_state.messages.append({
        "role": "assistant",
        "content": output_text
    })
