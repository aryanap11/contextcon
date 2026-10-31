import os
import json
import requests
from dotenv import load_dotenv
from crustdata_tools import analyze_company_footprint
import re

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def resolve_domain(user_query):
    """
    Uses Gemini to convert a messy natural language company name into a clean domain.
    Includes a bulletproof fallback for live demos.
    """
    # 1. Immediate Bypass: If the user already typed a domain, skip the AI entirely!
    if "." in user_query and " " not in user_query:
        return user_query.strip().lower()

    prompt = f"""
    You are an enterprise-grade Domain Resolution API. Your sole function is to parse messy, natural language text, identify the primary target entity, and return its canonical corporate website domain.

    STRICT OPERATIONAL DIRECTIVES:
    - Output EXACTLY ONE valid domain name.
    - NEVER include text, explanations, markdown formatting (```), quotes, or spaces.
    - Resolve subsidiaries to their primary operating domain.
    - Use recognized corporate domains for conglomerates (e.g., Tata Consultancy Services -> tcs.com).

    ROUTING MATRIX (FEW-SHOT EXAMPLES):

    # Category: Indian Tech & Quick Commerce
    Input: "that food delivery app swiggy" -> swiggy.com
    Input: "zeptonow quick grocery" -> zeptonow.com
    Input: "zomato food network" -> zomato.com
    Input: "ola cabs ride hailing" -> olacabs.com
    Input: "flipkart shopping" -> flipkart.com

    # Category: Indian Conglomerates & IT
    Input: "tata consultancy services" -> tcs.com
    Input: "reliance industries limited" -> ril.com
    Input: "infosys technologies" -> infosys.com
    Input: "wipro it services" -> wipro.com
    Input: "larsen and toubro" -> larsentoubro.com

    # Category: FinTech & Brokerage
    Input: "zerodha discount broker" -> zerodha.com
    Input: "groww mutual funds app" -> groww.in
    Input: "paytm one97 communications" -> paytm.com
    Input: "bharatpe merchant payments" -> bharatpe.com

    # Category: Global Tech & AI
    Input: "open ai chatgpt creator" -> openai.com
    Input: "anthropic claude" -> anthropic.com
    Input: "meta platforms facebook" -> meta.com

    # Category: VC, Holding Companies & Shells
    Input: "peak xv partners previously sequoia india" -> peakxv.com
    Input: "y combinator startup accelerator" -> ycombinator.com
    Input: "nexus venture partners" -> nexusvp.com
    Input: "tiger global management" -> tigerglobal.com

    LIVE QUERY:
    Input: "{user_query}"
    Output:
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            raw_text = response.json(
            )['candidates'][0]['content']['parts'][0]['text']

            # 2. Force Extraction: Rip out only the domain using regex
            match = re.search(r'([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', raw_text)
            if match:
                return match.group(1).lower()

            return raw_text.strip().lower()
    except Exception as e:
        # Prints to terminal so you know what happened
        print(f"Agent 1 Routing Error: {e}")

    # 3. HACKATHON FALLBACK: If Gemini rate-limits or fails, just guess!
    # "zomato" -> "zomato.com"


def run_osint_agent(domain):
    footprint_data = analyze_company_footprint(domain)

    if footprint_data.get("error"):
        return footprint_data

    # Strict, minimalist prompt for enterprise-grade reporting
    prompt = f"""
    You are a Tier-1 Corporate Intelligence AI.
    Generate a strict, minimalist, and highly professional due diligence report based on the provided OSINT data.
    
    OSINT DATA:
    {json.dumps(footprint_data, indent=2)}
    
    FORMAT REQUIREMENTS:
    - Use strict Markdown formatting.
    - NO introductory or concluding fluff (e.g., do not say "Here is the report").
    - Maintain a cold, objective, and forensic corporate tone.
    - Do not use the $ symbol for currency. Write "USD" instead to prevent Markdown rendering errors.
    
    REQUIRED SECTIONS:
    **1. Entity Overview**
    (1-2 sentences strictly defining the business context based on the description.)
    
    **2. Institutional Footprint Analysis**
    (Concise, analytical bullet points evaluating the headcount vs. funding ratio. Determine if this matches standard operational behavior, bootstrapped scale, or synthetic shell profiles.)
    
    **3. Final Verdict**
    (A single, bolded declaration: 'VERIFIED OPERATIONAL', 'HIGH-RISK ANOMALY', or 'SYNTHETIC ENTITY', followed by one sentence justifying the decision.)
    """

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            gemini_text = response.json(
            )['candidates'][0]['content']['parts'][0]['text']
            return {
                "error": False,
                "footprint_data": footprint_data,
                "agent_briefing": gemini_text
            }
        else:
            return {"error": True, "message": f"API Error: {response.text}"}
    except Exception as e:
        return {"error": True, "message": f"Connection failed: {str(e)}"}
