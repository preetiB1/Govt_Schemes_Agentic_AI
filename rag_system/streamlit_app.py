import streamlit as st
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from config import Config

# PAGE CONFIGURATION
st.set_page_config(
    page_title="SchemeKhoj - AI Agent",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

#  BEAUTIFICATION
st.markdown("""
<style>
    /* Main Title Styling */
    .main-title {
        font-size: 3rem;
        color: #FF9933; /* Saffronish */
        font-weight: 700;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 1.2rem;
        color: #cccccc; /* Light gray for dark mode readability */
        margin-bottom: 2rem;
    }
    
    /* Chat Bubble Styling */
    /* We target the container to force a light background with DARK text */
    [data-testid="stChatMessage"] {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        color: #1a1a1a !important; /* Force Black Text */
    }

    /* Force all inner text elements to be black */
    [data-testid="stChatMessage"] * {
        color: #1a1a1a !important;
    }

    /* Source Card Styling */
    .source-card {
        background-color: #f8f9fa;
        padding: 12px;
        border-radius: 8px;
        border-left: 5px solid #007bff;
        margin-bottom: 10px;
        color: #333 !important; /* Force text black in cards */
    }
    .source-title {
        font-weight: bold;
        color: #0056b3 !important;
        font-size: 1.05em;
    }
    .source-meta {
        font-size: 0.9em;
        color: #666 !important;
    }
    
    /* Make links visible */
    .source-card a {
        color: #007bff !important;
    }
</style>
""", unsafe_allow_html=True)

# SIDEBAR 
with st.sidebar:
    st.title("🏛️ SchemeKhoj AI")
    st.markdown("Your intelligent guide to Indian Government Schemes.")
    st.markdown("---")
    
    st.subheader("💡 Try these questions:")
    
    # Quick Action Buttons
    if st.button("🌾 Loans for Farmers"):
        st.session_state.initial_query = "What loan schemes are available for farmers in Tamil Nadu?"
    
    if st.button("🎓 Scholarships for Students"):
        st.session_state.initial_query = "List scholarships for engineering students."
        
    if st.button("👩‍💼 Schemes for Women"):
        st.session_state.initial_query = "What are the entrepreneurship schemes for women?"

    st.markdown("---")
    st.markdown("**Tech Stack:**")
    st.code("LangChain\nGoogle Gemini\nChromaDB\nStreamlit", language="text")
    st.caption("Created by Preeti Bhagtani")

# MAIN LOGIC 
@st.cache_resource
def load_resources():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    vector_db = Chroma(
        persist_directory=str(Config.CHROMA_DB_DIR),
        embedding_function=embeddings
    )
    
    llm = ChatGoogleGenerativeAI(
        model=Config.LLM_MODEL,
        google_api_key=Config.GOOGLE_API_KEY,
        temperature=0.3,
        convert_system_message_to_human=True
    )
    return vector_db, llm

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add a welcome message
    st.session_state.messages.append({
        "role": "assistant", 
        "content": "Namaste! 🙏 I am SchemeSetu. I can help you find government schemes tailored to your needs. Ask me anything!"
    })


try:
    vector_db, llm = load_resources()
except Exception as e:
    st.error(f"System Error: {e}")
    st.stop()

# MAIN UI 
st.markdown('<div class="main-title">🇮🇳 Government Schemes AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">RAG-Powered Semantic Search Engine</div>', unsafe_allow_html=True)

# Handle Button Clicks from Sidebar
if "initial_query" in st.session_state:
    user_input = st.session_state.initial_query
    del st.session_state.initial_query 
else:
    user_input = None

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        # If the message has sources attached (stored in session state differently usually, but keeping simple here)
        if "sources" in msg:
            with st.expander("📚 View Sources Referenced"):
                for source in msg["sources"]:
                    st.markdown(f"""
                    <div class="source-card">
                        <div class="source-title">{source['name']}</div>
                        <div class="source-meta">🔗 <a href="{source['url']}" target="_blank">Official Link</a></div>
                    </div>
                    """, unsafe_allow_html=True)

# Chat Input Handler
prompt = st.chat_input("Ex: Is there a subsidy for solar panels?")

# If button clicked OR user typed
if prompt or user_input:
    final_query = user_input if user_input else prompt
    
    # 1. Display User Message
    st.session_state.messages.append({"role": "user", "content": final_query})
    with st.chat_message("user"):
        st.markdown(final_query)

   # 2. Generate Answer
    with st.chat_message("assistant"):
        with st.spinner("🔍 Searching 100+ Government Schemes..."):
            try:
                # STEP A: RETRIEVAL
                docs = vector_db.similarity_search(final_query, k=3)
                
                # STEP B: MEMORY 
                # Get last 4 messages to give the AI context of the conversation
                chat_history_text = ""
                for msg in st.session_state.messages[:-1][-4:]:
                    role = "User" if msg["role"] == "user" else "Assistant"
                    chat_history_text += f"{role}: {msg['content']}\n"

                if not docs:
                    response_text = "I couldn't find any matching schemes in my database. Try broader keywords."
                    sources_data = []
                else:
                    # Context Building
                    context_text = "\n\n".join([
                        f"Scheme: {d.metadata.get('name', 'Unknown')}\nDetails: {d.page_content}" 
                        for d in docs
                    ])
                    
                    # STEP C: PROMPT WITH HISTORY 
                    full_prompt = f"""
                    You are a helpful assistant for Indian Government Schemes.
                    Answer the question based on the Context and Chat History below.
                    
                    1. Use the Context to answer the user's specific question.
                    2. Use the Chat History to understand follow-up questions (like "What are the benefits of that?").
                    3. If the answer isn't in the context, say so.

                    --- CHAT HISTORY ---
                    {chat_history_text}

                    --- CONTEXT FROM DATABASE ---
                    {context_text}

                    --- CURRENT QUESTION ---
                    {final_query}
                    """
                    
                    response = llm.invoke(full_prompt)
                    response_text = response.content
                    
                    # Prepare sources for UI
                    sources_data = [
                        {"name": d.metadata.get('name', 'Unknown'), "url": d.metadata.get('source', '#')}
                        for d in docs
                    ]

                # Display Answer
                st.markdown(response_text)
                
                # Display Sources nicely
                if sources_data:
                    with st.expander("📚 Referenced Schemes (Click to Open)"):
                        for s in sources_data:
                            st.markdown(f"**🔹 {s['name']}** \n🔗 [Official Source]({s['url']})")

                # Save to History
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response_text,
                    "sources": sources_data
                })

            except Exception as e:
                st.error(f"An error occurred: {e}")