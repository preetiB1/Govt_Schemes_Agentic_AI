import os
from langchain.tools import tool
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from config import Config


embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vector_db = None
if os.path.exists(Config.CHROMA_DB_DIR):
    vector_db = Chroma(
        persist_directory=str(Config.CHROMA_DB_DIR),
        embedding_function=embeddings
    )

translator_llm = ChatGroq(
    model=Config.LLM_MODEL,
    api_key=Config.GROQ_API_KEY,
    temperature=0
)

def english_to_simple_hindi(text: str) -> str:
    prompt = f"""
नीचे दिए गए सरकारी योजना विवरण को सरल हिंदी में समझाइए।
अंग्रेज़ी शब्द न रखें।

{text}
"""
    try:
        return translator_llm.invoke(prompt).content.strip()
    except:
        return text


@tool
def search_scheme_tool(query: str):
    """
    Used ONLY for initial scheme discovery.
    Returns short Hindi summaries.
    """
    if not vector_db:
        return "डेटाबेस उपलब्ध नहीं है।"

    docs = vector_db.similarity_search(query, k=2)
    if not docs:
        return "कोई उपयुक्त योजना नहीं मिली।"

    responses = []

    for i, d in enumerate(docs):
        raw = d.page_content

        first_sentence = raw.split(".")[0].strip() + "."
        hindi = english_to_simple_hindi(first_sentence)

        responses.append(
            f"योजना {i+1}: {d.metadata.get('scheme_name', 'अज्ञात')}\n"
            f"संक्षेप: {hindi}"
        )

    return "\n\n".join(responses)

@tool
def fetch_full_scheme_tool(scheme_name: str):
    """
    Returns FULL raw scheme text with section markers.
    Used for follow-up questions.
    """
    if not vector_db:
        return ""

    docs = vector_db.similarity_search(scheme_name, k=1)
    if not docs:
        return ""

    return docs[0].page_content


def extract_section_from_scheme(text: str, section: str) -> str:
    section = section.upper()

    markers = {
        "DESC": ("DESC:", "BENEFITS:"),
        "BENEFITS": ("BENEFITS:", "ELIGIBILITY:"),
        "ELIGIBILITY": ("ELIGIBILITY:", None)
    }

    if section not in markers:
        return "जानकारी उपलब्ध नहीं है।"

    start, end = markers[section]
    if start not in text:
        return "जानकारी उपलब्ध नहीं है।"

    content = text.split(start, 1)[1]
    if end and end in content:
        content = content.split(end, 1)[0]

    return content.strip()


@tool
def apply_for_scheme_tool(
    scheme_name: str = None,
    name: str = None,
    age: str = None,
    income: str = None,
    category: str = None,
    occupation: str = None,
    state: str = None
):
    """
    Submits a mock application for a government scheme.
    Requires complete applicant details and scheme name.
    """
    if not scheme_name:
        return "STOP! पहले योजना का नाम स्पष्ट करें।"

    missing = []
    if not name: missing.append("नाम")
    if not age: missing.append("उम्र")
    if not income: missing.append("आय")
    if not category: missing.append("श्रेणी")
    if not occupation: missing.append("पेशा")
    if not state: missing.append("राज्य")

    if missing:
        return f"STOP! निम्न जानकारी अधूरी है: {', '.join(missing)}"

    application_id = f"APP-{abs(hash(name)) % 100000}"

    return (
        "✅ आपका आवेदन सफलतापूर्वक जमा हो गया है।\n"
        f"योजना: {scheme_name}\n"
        f"आवेदन आईडी: {application_id}"
    )


tools = [
    search_scheme_tool,
    fetch_full_scheme_tool,
    apply_for_scheme_tool
]
