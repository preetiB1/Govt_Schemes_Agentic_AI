import os
import json
import shutil
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from config import Config 

def build_vector_db():
    documents = []
    if not os.path.exists(Config.NORMALIZED_DIR):
        print("❌ Data folder missing.")
        return

    files = [f for f in os.listdir(Config.NORMALIZED_DIR) if f.endswith(".json")]
    print(f"📂 Found {len(files)} JSON files. Preparing index...")

    for filename in files:
        try:
            with open(Config.NORMALIZED_DIR / filename, "r", encoding="utf-8") as f:
                data = json.load(f)

            page_content = (
                f"SCHEME: {data['scheme_name']}\n"
                f"DESC: {data['description']}\n"
                f"BENEFITS: {', '.join(data['benefits'])}\n"
                f"ELIGIBILITY: {', '.join(data['eligibility'])}"
            )

            meta = data['metadata']
            metadata = {
                "scheme_name": data['scheme_name'],
                "url": data.get("source_url", ""),
                "state": meta['state'],
                "min_age": int(meta['min_age']),
                "max_income": int(meta['max_income']),
                "beneficiary_type": meta['beneficiary_type']
            }

            documents.append(Document(page_content=page_content, metadata=metadata))

        except Exception as e:
            print(f"Skipping {filename}: {e}")

    if os.path.exists(Config.CHROMA_DB_DIR):
        shutil.rmtree(Config.CHROMA_DB_DIR)

    print("🧠 Generating Embeddings...")
    embedding_fn = HuggingFaceEmbeddings(model_name=Config.EMBEDDING_MODEL)

    print("🚀 Ingesting into ChromaDB...")
    Chroma.from_documents(
        documents=documents,
        embedding=embedding_fn,
        persist_directory=str(Config.CHROMA_DB_DIR)
    )
    print(f"✅ Database built at: {Config.CHROMA_DB_DIR}")

if __name__ == "__main__":
    build_vector_db()