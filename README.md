# Nexus Entity Intelligence

A simple due diligence dashboard that checks a company's actual headcount and funding against market data to flag basic anomalies. Built for automating corporate background checks and vendor screening.

## How It Works
1. **Input**: Enter a company's website domain (e.g., `zomato.com`).
2. **Data Pipeline**: Fetches ground-truth institutional data (verified headcount and total funding) using the Crustdata API.
3. **Anomaly Engine**: A deterministic Python backend calculates risk based on capital-to-employee ratios (e.g., flagging entities with massive funding but zero employees).
4. **AI Reporting**: Passes the structured JSON data to the Gemini API to generate a readable, forensic executive summary.

## Tech Stack
* **Frontend**: Streamlit
* **Backend Data**: Crustdata API
* **LLM / Reporting**: Google Gemini API
* **Language**: Python

## Setup and Installation

**1. Clone the repository**
```bash
git clone <your-repo-link-here>
cd <your-repo-folder-name>

python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

pip install streamlit requests python-dotenv

CRUSTDATA_API_KEY=your_crustdata_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

python -m streamlit run app.py
