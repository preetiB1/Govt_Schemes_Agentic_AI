import os
import csv
import time
import json
import requests
import sys


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List
from config import Config

#DATA STRUCTURE 
class SchemeMetadata(BaseModel):
    min_age: int = Field(description="Minimum eligible age (0 if not specified)")
    max_income: int = Field(description="Maximum income limit in INR (99999999 if not specified)")
    state: str = Field(description="The state name (e.g., 'Tamil Nadu') or 'Central'")
    beneficiary_type: str = Field(description="Main target: 'Student', 'Farmer', 'Woman', 'Disabled', 'General'")

class SchemeSchema(BaseModel):
    scheme_name: str = Field(description="Official name of the scheme")
    description: str = Field(description="A concise summary")
    benefits: List[str] = Field(description="List of benefits")
    eligibility: List[str] = Field(description="List of eligibility rules")
    documents: List[str] = Field(description="List of required documents")
    metadata: SchemeMetadata = Field(description="Structured fields for filtering")

def process_schemes():
    # LANGCHAIN SETUP 
   
    llm = ChatGoogleGenerativeAI(
        model=Config.LLM_MODEL, 
        temperature=0,
        google_api_key=Config.GOOGLE_API_KEY,
        max_retries=0  
    )
    
    parser = JsonOutputParser(pydantic_object=SchemeSchema)
    
    prompt = PromptTemplate(
        template="""
        You are a Data Extraction Agent. Extract structured JSON.
        {format_instructions}
        
        --- TEXT ---
        {raw_text}
        """,
        input_variables=["raw_text"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    chain = prompt | llm | parser

    if not os.path.exists(Config.LINKS_FILE):
        print("❌ CSV not found. Run script 01 first.")
        return

    with open(Config.LINKS_FILE, "r") as f:
        reader = csv.reader(f)
        next(reader)
        links = [row[0] for row in reader]

    os.makedirs(Config.NORMALIZED_DIR, exist_ok=True)
    
    print(f"🚀 Processing {len(links)} schemes (LangChain Mode)...")
    
    for i, link in enumerate(links):
        scheme_id = link.strip("/").split("/")[-1]
        out_path = Config.NORMALIZED_DIR / f"{scheme_id}.json"
        
        if os.path.exists(out_path):
            continue 

        #  Jina Fetching
        raw_text = None
        for attempt in range(3):
            try:
                jina_url = f"{Config.JINA_BASE_URL}{link}"
                headers = {"Authorization": f"Bearer {Config.JINA_API_KEY}"} if Config.JINA_API_KEY else {}
                resp = requests.get(jina_url, headers=headers, timeout=30)
                if resp.status_code == 200:
                    raw_text = resp.text[:30000]
                    break
                time.sleep(2)
            except:
                time.sleep(2)
        
        if not raw_text:
            print(f"❌ Skipping {scheme_id} (Jina failed)")
            continue

       
        retry_count = 0
        max_attempts = 5
        success = False
        
        while not success and retry_count < max_attempts:
            try:
                # LangChain Invoke
                data = chain.invoke({"raw_text": raw_text})
                data["source_url"] = link
                
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                print(f"✅ [{i+1}/{len(links)}] Saved: {scheme_id}")
                success = True
                time.sleep(2) 

            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "Quota" in error_msg or "ResourceExhausted" in error_msg:
                    print(f"🛑 Quota Hit! Sleeping for 60 seconds...")
                    time.sleep(60) 
                    retry_count += 1
                else:
                    print(f"❌ Real Error on {scheme_id}: {e}")
                    break 

if __name__ == "__main__":
    process_schemes()