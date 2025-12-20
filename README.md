Here is a comprehensive README.md for your GitHub repository. It covers the architecture, setup, usage, and features based on the code provided.

🇮🇳 SchemeKhoj - Voice-Based AI Agent for Government Schemes
SchemeKhoj is a voice-first, vernacular AI agent designed to help Indian users identify and apply for government welfare schemes in Hindi.
Built as part of an AI/ML Design Assignment, this system bridges the digital divide by allowing users to interact naturally using their voice, overcoming language and literacy barriers.

🎥 Demo
https://drive.google.com/file/d/1asfCrRF8oJNy1xvvOoaV2fQpXhhjHjkT/view?usp=sharing


🚀 Key Features
1. Voice-First Interaction: Users can speak in Hindi to search for schemes. The system listens, processes, and responds with synthesized speech (Text-to-Speech).

2. RAG-Based Knowledge Base: Uses Retrieval Augmented Generation (RAG) to fetch accurate scheme details from a curated vector database.

3. Agentic Workflow: Implements a Finite State Machine (FSM) (Planner-Executor pattern) to handle complex conversations (Search → Info → Data Collection → Application).

4. Vernacular Support: Full pipeline support for Hindi (Input processing, LLM reasoning, and TTS output).

5. Automated Data Pipeline: Includes scripts to scrape myscheme.gov.in, extract structured data using LLMs, and build a ChromaDB vector index.

6. Tool Usage: The agent autonomously decides when to search the database, fetch full details, or trigger a mock application process.

🏗️ Architecture
The system consists of two main components:

Data Pipeline:
Scraping: Selenium extracts scheme URLs.
Extraction: Jina AI fetches raw text; Google Gemini extracts structured JSON (Eligibility, Benefits, etc.).
Indexing: HuggingFace Embeddings + ChromaDB store the data for semantic search.

Agent Application:
Frontend: Streamlit with speech_recognition and gTTS.
Brain: A State Machine Agent using Groq (Llama 3) for intent classification and translation.

Tools: Custom tools for vector search and mock application submission.

Project Structure: 
├── 01_scrape_urls.py      # Selenium script to scrape scheme URLs
├── 02_extract_data.py     # ETL pipeline: Jina (fetch) -> Gemini (structure) -> JSON
├── 03_build_db.py         # Vector DB builder (ChromaDB + HuggingFace)
├── agentt.py              # Main Streamlit Application (Frontend)
├── state_agent.py         # Finite State Machine Logic (The "Brain")
├── agent_tools.py         # LangChain Tools (Search, Apply, Translate)
├── config.py              # Configuration & Environment Variables
└── requirements.txt       # Dependencies

Installation & Setup
1. Clone the Repository
git clone https://github.com/preetiB1/Govt_Schemes_Agentic_AI.git
2. Install Dependencies
Ensure you have Python 3.9+ installed.
pip install -r requirements.txt

3. Set Up Environment Variables
Create a config.py file or set environment variables for the following API keys:

GROQ_API_KEY: For the Agent's reasoning (Llama 3).
GOOGLE_API_KEY: For Data Extraction (Gemini).
JINA_API_KEY: For fetching web content.



How to Run
Step 1: Build the Knowledge Base (Optional if DB exists)
If you want to build the database from scratch:
# 1. Scrape URLs
python 01_scrape_urls.py

# 2. Extract Data (LLM Processing)
python 02_extract_data.py

# 3. Build Vector Database
python 03_build_db.py

Step 2: Run the Voice Agent
Launch the Streamlit interface:
streamlit run agentt.py

Usage Guide
Tap to Speak: Click the microphone button and ask a question in Hindi.
Example: "किसानों के लिए लोन योजना बताओ" (Tell me loan schemes for farmers).
Listen: The agent will respond with audio and text.
Explore: You can ask for details like "Benefits" (लाभ), "Eligibility" (पात्रता), or "Documents" (दस्तावेज़).
Apply: Say "मुझे आवेदन करना है" (I want to apply). The agent will ask for details (Name, Age, Income, etc.) and submit a mock application.

🧩 Tech Stack
LLMs: Llama 3 (via Groq), Gemini Pro (via Google GenAI)
Vector Database: ChromaDB
Embeddings: HuggingFace (all-MiniLM-L6-v2)
Frameworks: LangChain, Streamlit
Speech: Google Speech Recognition (STT), gTTS (TTS)
Scraping: Selenium, Jina AI
