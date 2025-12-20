from typing import Dict, Optional
from agent_tools import search_scheme_tool, apply_for_scheme_tool, extract_section_from_scheme
from langchain_groq import ChatGroq
from config import Config

START = "START"
CONFIRM = "CONFIRM"
COLLECT = "COLLECT"
APPLY = "APPLY"
END = "END"


intent_llm = ChatGroq(
    model=Config.LLM_MODEL,
    api_key=Config.GROQ_API_KEY,
    temperature=0
)

def classify_intent_hindi(text: str) -> str:
    prompt = f"""
यूज़र का इरादा पहचानिए।
केवल एक शब्द लौटाएँ: SEARCH, INFO, APPLY, NO

INFO तब जब यूज़र लाभ, पात्रता, दस्तावेज़ पूछे
APPLY तब जब यूज़र आवेदन करना चाहे

वाक्य: "{text}"
"""
    try:
        return intent_llm.invoke(prompt).content.strip().upper()
    except:
        return "SEARCH"


class SchemeAgent:
    def __init__(self):
        self.state = START
        self.user_data: Dict[str, str] = {}
        self.selected_scheme: Optional[str] = None

    def step(self, user_input: str):
        intent = classify_intent_hindi(user_input)
        text_lower = user_input.lower()

        if self.state == START:
            self.state = CONFIRM
            self.selected_scheme = user_input
            return {
                "action": "SEARCH",
                "query": user_input
            }

        if self.state == CONFIRM:

            if intent == "INFO" and self.selected_scheme:
                full_text = search_scheme_tool(self.selected_scheme)

                if any(k in text_lower for k in ["लाभ", "benefit"]):
                    return extract_section_from_scheme(full_text, "BENEFITS")

                if any(k in text_lower for k in ["eligibility", "पात्रता"]):
                    return extract_section_from_scheme(full_text, "ELIGIBILITY")

                if any(k in text_lower for k in ["क्या है", "details", "desc"]):
                    return extract_section_from_scheme(full_text, "DESC")

                return (
                    "आप इस योजना के लाभ, पात्रता या दस्तावेज़ के बारे में पूछ सकते हैं।\n"
                    "यदि आवेदन करना हो तो 'आवेदन करना है' कहें।"
                )

            if intent == "APPLY":
                self.state = COLLECT
                return (
                    "ठीक है। कृपया यह जानकारी comma से अलग करके दें:\n"
                    "नाम, उम्र, आय, श्रेणी, पेशा, राज्य"
                )

            if intent == "NO":
                self.state = END
                return "ठीक है। यदि और सहायता चाहिए तो बताइए।"

            return (
                "क्या आप केवल जानकारी चाहते हैं या आवेदन करना चाहते हैं?\n"
                "कहिए: 'लाभ बताओ' या 'आवेदन करना है'"
            )

        if self.state == COLLECT:
            parts = [p.strip() for p in user_input.split(",")]

            if len(parts) < 6:
                return "जानकारी अधूरी है। कृपया सभी विवरण दें।"

            self.user_data = {
                "name": parts[0],
                "age": parts[1],
                "income": parts[2],
                "category": parts[3],
                "occupation": parts[4],
                "state": parts[5],
            }

            payload = {
                "scheme_name": self.selected_scheme or "चयनित योजना",
                "name": self.user_data["name"],
                "age": self.user_data["age"],
                "income": self.user_data["income"],
                "category": self.user_data["category"],
                "occupation": self.user_data["occupation"],
                "state": self.user_data["state"],
            }

            self.state = APPLY
            return apply_for_scheme_tool.invoke(payload)

        return "धन्यवाद।"
