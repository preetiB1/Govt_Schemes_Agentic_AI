import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API KEYS
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    JINA_API_KEY = os.getenv("JINA_API_KEY")

    # MODELS
    LLM_MODEL = "llama-3.1-8b-instant"
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

    # PATHS 
    BASE_DIR = Path(__file__).parent
    
    SCRIPTS_DIR = BASE_DIR / "scripts"
    LINKS_FILE = SCRIPTS_DIR / "myscheme_links.csv"
    
    DATA_DIR = BASE_DIR / "Data"
    NORMALIZED_DIR = DATA_DIR / "Normalized"
    
    CHROMA_DB_DIR = BASE_DIR / "chroma_db_store"

    # --- SETTINGS ---
    JINA_BASE_URL = "https://r.jina.ai/"
    TOP_K_RESULTS = 5
